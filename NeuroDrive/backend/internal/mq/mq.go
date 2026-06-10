package mq

import (
	"github.com/streadway/amqp"
)

type Mq struct {
	conn    *amqp.Connection
	channel *amqp.Channel
	queue   string
}

func NewMq(url, queue string) (*Mq, error) {
	conn, err := amqp.Dial(url)
	if err != nil {
		return nil, err
	}
	ch, err := conn.Channel()
	if err != nil {
		conn.Close()
		return nil, err
	}
	_, err = ch.QueueDeclare(
		queue,
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		ch.Close()
		conn.Close()
		return nil, err
	}
	return &Mq{
		conn:    conn,
		channel: ch,
		queue:   queue,
	}, nil
}

func (mq *Mq) ReadMessages() (<-chan amqp.Delivery, error) {
	msgs, err := mq.channel.Consume(
		mq.queue,
		"",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return nil, err
	}
	return msgs, nil
}

func (mq *Mq) Close() {
	if mq.channel != nil {
		mq.channel.Close()
	}
	if mq.conn != nil {
		mq.conn.Close()
	}
}
