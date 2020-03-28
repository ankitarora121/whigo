import whigo

whigo.initialize()

def test_foo():
    @whigo.scope()
    def foo():
        print('ankit')

    foo()



def test_bar():
    with whigo.scope('yolo') as ws:
        print("yo")
        ws.add_params(ankit='aorra')
        raise Exception



def test_yolo():
    whigo.config.set({
        'elasticsearch': {
            'host': 'search-maitri-aws-es-bnwhwr7beazoh6dudncdymqanm.us-east-2.es.amazonaws.com',
            'port': 443
        }
    })
    for i in range(100):
        with whigo.scope('swag') as ws:
            print("yo")
            ws.add_params(ankit='aorra')
