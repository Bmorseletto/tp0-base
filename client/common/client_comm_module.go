package common

import (
	"encoding/binary"
	"net"
)

const PROTOCOL = "tcp"
const U32_BYTES = 4

// Communication module Entity that encapsulates communication with server
type CommModule struct {
	conn net.Conn
}

func NewModule() *CommModule {
	module := &CommModule{
		conn: nil,
	}
	return module
}

// Connect Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (m *CommModule) Connect(serverAdress string) error {
	conn, err := net.Dial(PROTOCOL, serverAdress)
	if err != nil {
		return err
	}
	m.conn = conn
	return nil
}

func (m *CommModule) Close() {
	m.conn.Close()
}

func (m *CommModule) send_message(message string) error {
	message_bytes := []byte(message)
	message_len := uint32(len(message_bytes))
	len_header := make([]byte, U32_BYTES)
	binary.BigEndian.PutUint32(len_header, message_len)
	err := send_bytes(m.conn, len_header, U32_BYTES)
	if err != nil {
		return err
	}
	err = send_bytes(m.conn, message_bytes, message_len)
	if err != nil {
		return err
	}
	return nil
}

func send_bytes(conn net.Conn, message []byte, message_len uint32) error {
	bytes_sent := uint32(0)
	for bytes_sent != message_len {
		n, err := conn.Write(message[bytes_sent:])
		bytes_sent += uint32(n)
		if err != nil {
			return err
		}
	}
	return nil
}

func (m *CommModule) receive_message() (string, error) {
	message_len_bytes, err := receive_bytes(m.conn, 4)
	message_len := binary.BigEndian.Uint32(message_len_bytes)
	if err != nil {
		return "", err
	}
	message, err := receive_bytes(m.conn, message_len)
	if err != nil {
		return "", err
	}
	return string(message), err
}

func receive_bytes(conn net.Conn, message_len uint32) ([]byte, error) {
	bytes_recived := uint32(0)
	message := make([]byte, U32_BYTES)
	for bytes_recived != message_len {
		buffer := make([]byte, U32_BYTES)
		n, err := conn.Read(buffer)
		if err != nil {
			return nil, err
		}
		bytes_recived += uint32(n)
		message = append(message, buffer...)
	}
	return message, nil
}
