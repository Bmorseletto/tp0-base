package common

import (
	"bufio"
	"context"
	"fmt"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

const MAX_BATCH_BYTES = 8192
const NAME = 0
const LASTNAME = 1
const DNI = 2
const BIRTHDATE = 3
const NUMBER = 4

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID             string
	ServerAddress  string
	LoopAmount     int
	LoopPeriod     time.Duration
	MaxBatchAmount int
	Bets           string
	CurrentMessage string
}

// Client Entity that encapsulates how
type Client struct {
	config          ClientConfig
	conn            *CommModule
	sulprus_message string
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config:          config,
		conn:            NewModule(),
		sulprus_message: "",
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
	f, err := os.Open(c.config.Bets)
	if err != nil {
		log.Errorf("action: open_bets_csv | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}
	scanner := bufio.NewScanner(f)
	scanner.Split(bufio.ScanLines)
	for batch := 1; batch <= c.config.LoopAmount && c.sulprus_message != ""; batch++ {
		// Create the connection the server in every loop iteration. Send an
		select {
		case <-ctx.Done():
			log.Infof("closing client")
			return
		default:
			c.prepare_message(scanner)
			if c.config.CurrentMessage == "" {
				break
			}
			if !c.send_message(batch) {
				return
			}
		}

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}

func (c *Client) prepare_message(scanner *bufio.Scanner) {
	if c.sulprus_message != "" {
		c.config.CurrentMessage += c.sulprus_message
		c.sulprus_message = ""
	}
	batch_counter := 0
	for scanner.Scan() {
		line := scanner.Text()
		bet_data := strings.Split(line, ",")
		new_bet := fmt.Sprintf(
			"Client:%s|Name:%s|LastName:%s|Dni:%v|Birthdate:%s|Number:%v\n",
			c.config.ID,
			bet_data[NAME],
			bet_data[LASTNAME],
			bet_data[DNI],
			bet_data[BIRTHDATE],
			bet_data[NUMBER],
		)
		if MAX_BATCH_BYTES < len([]byte(c.config.CurrentMessage+new_bet)) {
			c.sulprus_message = new_bet
			return
		}
		c.config.CurrentMessage += new_bet
		batch_counter += 1
		if batch_counter == c.config.MaxBatchAmount {
			return
		}

	}
}

func (c *Client) send_message(msgID int) bool {
	c.createClientSocket()
	err := c.conn.send_message(c.config.CurrentMessage)
	c.conn.Close()

	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return false
	}

	/*log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
		c.config.Dni,
		c.config.Number,
	)*/
	c.config.CurrentMessage = ""
	// Wait a time between sending one message and the next one
	time.Sleep(c.config.LoopPeriod)
	return true
}
