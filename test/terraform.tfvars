deployment = {
nodered = {
  image = "nodered/node-red:latest"
  ports = [{
    internal = 1980
    external = 1980
    protocol = "tcp"
  },
  {
  internal = 1981
  external = 1981
  protocol = "tcp"
  }]
}
influxdb = {
  image = "influx/influxdb:latest"
  ports = [{
    internal = 3200
    external = 3200
    protocol = "tcp"
  }]
}
}