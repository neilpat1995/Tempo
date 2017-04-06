import lasagne
import theano
import theano.tensor as T

def rectify():
    return lasagne.nonlinearities.rectify

def leaky_rectify():
    return lasagne.nonlinearities.leaky_rectify

def softmax():
    return lasagne.nonlinearities.softmax

class ConvNeuralNet(object):
    def __init__(self, params = None):
        self.inputs = T.tensor4('inputs')

        self.net = lasagne.layers.InputLayer(
            #shape = (None, 1, 646, 128),
            shape = (None, 1, 969, 128),
            #shape = (None, 1, 1025, 969),
            input_var = self.inputs
        )

    def with_conv_layer(self, filter_size, num_filters):
        self.net = lasagne.layers.Conv2DLayer(
            self.net,
            num_filters = num_filters,
            filter_size = filter_size,
            nonlinearity = lasagne.nonlinearities.rectify
        )

        return self

    def with_max_pooling_layer(self, pool_size):
        self.net = lasagne.layers.MaxPool2DLayer(
            self.net,
            pool_size = pool_size
        )

        return self

    def with_dense_layer(self, dropout_rate, num_nodes):
        self.net = lasagne.layers.DenseLayer(
            lasagne.layers.dropout(self.net, p = dropout_rate),
            num_units = num_nodes,
            nonlinearity = lasagne.nonlinearities.rectify
        )

        return self

    def with_output_layer(self, dropout_rate, num_labels):
        self.net = lasagne.layers.DenseLayer(
            lasagne.layers.dropout(self.net, p = dropout_rate),
            num_units = num_labels,
            nonlinearity = lasagne.nonlinearities.softmax
        )

        return self

    def with_reg_layer(self, dropout_rate, num_labels):
        self.net = lasagne.layers.DenseLayer(
            lasagne.layers.dropout(self.net, p = dropout_rate),
            num_units = num_labels,
            nonlinearity = lasagne.nonlinearities.linear
        )

        return self

    @property
    def params(self):
        return lasagne.layers.get_all_param_values(self.net)

    @params.setter
    def params(self, params):
        lasagne.layers.set_all_param_values(self.net, params)

def build_user_net():
    net = ConvNeuralNet()
    net = net.with_conv_layer(filter_size = (4, 128), num_filters = 256).with_max_pooling_layer(pool_size = (4, 1))
    net = net.with_conv_layer(filter_size = (4, 1), num_filters = 256).with_max_pooling_layer(pool_size = (4, 1))
    net = net.with_dense_layer(dropout_rate = 0.5, num_nodes = 256)
    net = net.with_output_layer(dropout_rate = 0.5, num_labels = 2)

    return net
