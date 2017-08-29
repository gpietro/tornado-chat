import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen as gen

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)

# we gonna store clients in dictionary..
clients = set()

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render('index.html')
        # self.write("This is your response")
        # we don't need self.finish() because self.render() is fallowed by self.finish() inside tornado 
        # self.finish()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        self.id = self.get_argument("Id")
        self.stream.set_nodelay(True)
        clients.add(self)


    def on_message(self, message):        
        self.broadcast_message("You said: " + message)
        
    def on_close(self):
        clients.remove(self)

    @gen.coroutine
    def broadcast_message(self, message):
        count = 0
        for client in clients:
            client.write_message(message)
            count += 1
            if count % 100 == 0:
                yield gen.moment


app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/ws', WebSocketHandler),
])


if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()