#!/usr/bin/env python3

import flask, os, sys, time, psutil, json, socket
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from multiprocessing import Process, Manager

try :
	PORT = sys.argv[1]
except :
	PORT = 9890

if getattr(sys, 'frozen', None):
	static = os.path.join(sys._MEIPASS, 'static')
else:
	static = 'static'

app = flask.Flask(__name__, static_folder=static)

@app.route('/')
def frontend():
	return flask.send_from_directory(app.static_folder, 'index.html')

@app.route('/raw')
def raw():
	return flask.Response(
		json.dumps(stats.copy()),
		mimetype='application/json'
	)

def update(stats):
	while True:
		diskused = 0
		disktotal = 0
		for i in psutil.disk_partitions():
			try:
				x = psutil.disk_usage(i.mountpoint)
				diskused += x.used
				disktotal += x.total
			except OSError:
				pass
		stats['uptime'] = time.time() - psutil.boot_time()
		stats['fqdn'] = socket.gethostname()
		stats['cpuusage'] = psutil.cpu_percent(0)
		stats['ramusage'] = psutil.virtual_memory()
		stats['diskio'] = psutil.disk_io_counters()
		stats['diskusage'] = [diskused, disktotal]
		stats['netio'] = psutil.net_io_counters()
		stats['swapusage'] = psutil.swap_memory()
		time.sleep(1)

if __name__ == '__main__':
	stats = Manager().dict()
	Process(target=update, args=(stats, )).start()
	server = HTTPServer(WSGIContainer(app))
	print('Listening on port ' + str(PORT))
	server.listen(PORT)
	IOLoop.instance().start()
