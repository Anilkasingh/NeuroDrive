package main

import (
	"bufio"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"go.bug.st/serial"
)

// dir is the directory in which recordings are stored
// it will be the timestamp at which recording begins,
// in order to prevent clashes
var dir string

func main() {
	// Set up serial port
	mode := &serial.Mode{
		BaudRate: 115200,
		DataBits: 8,
		Parity:   serial.NoParity,
		StopBits: serial.OneStopBit,
	}

	port, err := serial.Open("/dev/ttyS4", mode)
	if err != nil {
		log.Fatal("Error opening serial port: ", err)
	}
	defer port.Close()

	done := make(chan os.Signal, 1)
	// notify when file is done processing
	finish := make(chan any, 1)

	//gracefully handle Ctrl+C
	signal.Notify(done, syscall.SIGINT, syscall.SIGTERM)

	fmt.Println("Recording data... Press Ctrl+C to stop")

	scanner := bufio.NewScanner(port)

	//setup output dir
	dir = strconv.FormatInt(time.Now().UnixMilli(), 10)

	if err := os.Mkdir(dir, 0770); err != nil {
		log.Fatalln(err.Error())
	}

	file, err := os.Create(dir + "/exg_0.csv")
	if err != nil {
		log.Println(err.Error())
		return
	}

	inc := 0

	writer := csv.NewWriter(file)
	writer.Write([]string{"timestamp", "eeg", "ecg"})

	readflag := false

	for {
		select {
		case <-done:
			fmt.Println("\nStopping recording...")
			writer.Flush()
			file.Close()
			return
		case <-finish:
			writer.Flush()
			log.Println(fmt.Sprintf("Written exg_%v.csv", inc))
			file.Close()
			inc++

			//open next csv
			file, err = os.Create(dir + fmt.Sprintf("/exg_%v.csv", inc))
			if err != nil {
				log.Fatalln(err.Error())
			}
			writer = csv.NewWriter(file)
			writer.Write([]string{"timestamp", "eeg", "ecg"})
		default:
			if scanner.Scan() {
				line := scanner.Text()
				timestamp := time.Now().UnixMilli()

				if !readflag {
					if line == "START" {
						log.Println("starting")
						readflag = true
					}
					continue
				}

				if line == "END" {
					finish <- 0
					readflag = false
					continue
				}

				//in the format eeg|ecg
				//spl := strings.Split(line, "|")
				writer.Write([]string{
					strconv.FormatInt(timestamp, 10),
					//spl[0],
					line,
				})
				writer.Flush()
			}
			if err := scanner.Err(); err != nil {
				log.Println("Serial read error:", err)
			}
		}
	}
}
