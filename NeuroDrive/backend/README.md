To run:

Pull TimescaleDB image and run it
```sh
$ docker compose up -d
```

Apply migrations
```sh
$ goose up
```

> Need to have goose installed

```sh
$ go install github.com/pressly/goose/v3/cmd/goose@latest
```

Run backend
```sh
$ go run cmd/web/*.go
```

or in Powershell
```powershell
$ go run .\cmd\web\.
```