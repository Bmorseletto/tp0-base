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
