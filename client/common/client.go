package common

import (
	"context"
	"fmt"
	"os/signal"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	Name          string
	LastName      string
	Dni           int
	Birthdate     string
	Number        int
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   *CommModule
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
		conn:   NewModule(),
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	err := c.conn.Connect(c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGTERM)
	defer stop()
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; msgID <= c.config.LoopAmount; msgID++ {
		// Create the connection the server in every loop iteration. Send an
		select {
		case <-ctx.Done():
			log.Infof("closing client")
			return
		default:
			if !c.send_message(msgID) {
				return
			}
		}

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}

func (c *Client) send_message(msgID int) bool {
	c.createClientSocket()
	message := fmt.Sprintf(
		"Client:%s|Name:%s|LastName:%s|Dni:%v|Birthdate:%s|Number:%v",
		c.config.ID,
		c.config.Name,
		c.config.LastName,
		c.config.Dni,
		c.config.Birthdate,
		c.config.Number,
	)
	err := c.conn.send_message(message)
	c.conn.Close()

	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return false
	}

	log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
		c.config.Dni,
		c.config.Number,
	)

	// Wait a time between sending one message and the next one
	time.Sleep(c.config.LoopPeriod)
	return true
}
