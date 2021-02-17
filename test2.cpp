// Based on code from https://blog.mbedded.ninja/programming/operating-systems/linux/linux-serial-ports-using-c-cpp/#basic-setup-in-c

#include <vector>
#include <string>
#include <iostream>
#include <fstream>
#include <stdexcept>

// C library headers
//#include <cstdio>
#include <cstring>

// Linux headers
#include <fcntl.h> // Contains file controls like O_RDWR
#include <termios.h> // Contains POSIX terminal control definitions
#include <unistd.h> // write(), read(), close()


class USBSerial
{
public:
  USBSerial(const std::string& device)
  {
    // Open the serial port. Change device path as needed (currently set to an standard FTDI USB-UART cable type device)
    serial_port = open(device.c_str(), O_RDWR);

    // Read in existing settings, and handle any error
    if(tcgetattr(serial_port, &tty) != 0)
    {
      throw std::runtime_error("Error %i from tcgetattr: %s\n"); //, errno, strerror(errno));
    }

    tty.c_cflag &= ~PARENB; // Clear parity bit, disabling parity (most common)
    tty.c_cflag &= ~CSTOPB; // Clear stop field, only one stop bit used in communication (most common)
    tty.c_cflag &= ~CSIZE; // Clear all bits that set the data size
    tty.c_cflag |= CS8; // 8 bits per byte (most common)
    tty.c_cflag &= ~CRTSCTS; // Disable RTS/CTS hardware flow control (most common)
    tty.c_cflag |= CREAD | CLOCAL; // Turn on READ & ignore ctrl lines (CLOCAL = 1)

    tty.c_lflag &= ~ICANON;
    tty.c_lflag &= ~ECHO; // Disable echo
    tty.c_lflag &= ~ECHOE; // Disable erasure
    tty.c_lflag &= ~ECHONL; // Disable new-line echo
    tty.c_lflag &= ~ISIG; // Disable interpretation of INTR, QUIT and SUSP
    tty.c_iflag &= ~(IXON | IXOFF | IXANY); // Turn off s/w flow ctrl
    tty.c_iflag &= ~(IGNBRK|BRKINT|PARMRK|ISTRIP|INLCR|IGNCR|ICRNL); // Disable any special handling of received bytes

    tty.c_oflag &= ~OPOST; // Prevent special interpretation of output bytes (e.g. newline chars)
    tty.c_oflag &= ~ONLCR; // Prevent conversion of newline to carriage return/line feed
    // tty.c_oflag &= ~OXTABS; // Prevent conversion of tabs to spaces (NOT PRESENT ON LINUX)
    // tty.c_oflag &= ~ONOEOT; // Prevent removal of C-d chars (0x004) in output (NOT PRESENT ON LINUX)

    tty.c_cc[VTIME] = 10;    // Wait for up to 1s (10 deciseconds), returning as soon as any data is received.
    tty.c_cc[VMIN] = 0;

    // Set in/out baud rate
    cfsetispeed(&tty, B115200);
    cfsetospeed(&tty, B115200);

    // Save tty settings, also checking for error
    if (tcsetattr(serial_port, TCSANOW, &tty) != 0)
    {
      throw std::runtime_error("Error %i from tcsetattr: %s\n"); //, errno, strerror(errno));
    }
  }

  bool read(std::string& buf)
  {
    // Read bytes. The behaviour of read() (e.g. does it block?,
    // how long does it block for?) depends on the configuration
    // settings above, specifically VMIN and VTIME
    return ::read(serial_port, buf.data(), buf.size()) >= 0;
  }

  void write_buf(const std::vector<uint8_t> bytes)
  {
    ssize_t ret = ::write(serial_port, bytes.data(), bytes.size());
    if (ret < 0)
      throw std::runtime_error("write buf failure");
  }

  // only meant for POD types
  template<typename T>
  bool write(T val)
  {
    return ::write(serial_port, &val, sizeof(T)) >= 0;
  }

  ~USBSerial()
  {
    close(serial_port);
  }

private:
  int serial_port;
  termios tty;
};


int main()
{
  try {
    USBSerial pico("/dev/ttyACM0");
    std::string read_buf(256, 0);

    std::cout << "[H] send 'h'" << std::endl;
    pico.write('h');

    std::ifstream file("test2.txt", std::ios::in | std::ios::binary);
    std::vector<uint8_t> data{std::istreambuf_iterator<char>(file), std::istreambuf_iterator<char>()};

    std::cout << "[H] send size: " << data.size() << std::endl;
    pico.write(data.size());

    pico.read(read_buf);
    printf("[D] %s\n", read_buf.c_str());

    pico.read(read_buf);
    printf("[D] %s\n", read_buf.c_str());

    std::cout << "[H] sending bytes " << data.size() << std::endl;
    pico.write_buf(data);

    pico.read(read_buf);
    printf("[D] %s\n", read_buf.c_str());

  }
  catch(std::exception& e)
  {
    std::cout << e.what() << std::endl;
    return 1;
  }
  catch(...)
  {
    return 2;
  }
}