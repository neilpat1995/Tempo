import lasagne
import numpy as np
import theano
import theano.tensor as T

def _iterate_batch(inputs, targets, batch_size, shuffle = False):
    assert len(inputs) == len(targets) and batch_size <= len(inputs)

    n = len(inputs)

    if shuffle:
        indices = np.arange(n)
        np.random.shuffle(indices)

    for i in range(0, n - batch_size + 1, batch_size):
        subset = indices[i:i + batch_size] if shuffle else slice(i, i + batch_size)
        yield inputs[subset], targets[subset]

class NeuralNetTrainingResult(object):
    def __init__(self):
        self.test_loss = None
        self.test_accuracy = None
        self.training_losses = []
        self.validation_losses = []
        self.validation_accuracies = []

class NeuralNetTrainer(object):
    def __init__(self, net):
        self._net = net
        
    def train(self, train_inputs, train_targets, 
              val_inputs = None, val_targets = None, 
              test_inputs = None, test_targets = None, 
              learning_rate = 0.01, momentum = 0.5,
              batch_size = 20, iterations = 100):
        inputs_var = self._net.inputs
        targets_var = T.ivector('targets')
        prediction = lasagne.layers.get_output(self._net.net)
        loss = lasagne.objectives.categorical_crossentropy(prediction, targets_var).mean()
        
        params = lasagne.layers.get_all_params(self._net.net, trainable = True)
        updates = lasagne.updates.nesterov_momentum(
            loss,
            params,
            learning_rate = learning_rate,
            momentum = momentum
        )

        test_prediction = lasagne.layers.get_output(self._net.net, deterministic = True)
        test_loss = lasagne.objectives.categorical_crossentropy(test_prediction, targets_var).mean()

        test_acc = T.mean(
            T.eq(T.argmax(test_prediction, axis = 1), targets_var),
            dtype = theano.config.floatX
        )

        train_func = theano.function([inputs_var, targets_var], loss, updates = updates, allow_input_downcast = True)
        val_func = theano.function([inputs_var, targets_var], [test_loss, test_acc], allow_input_downcast = True)


        ret = NeuralNetTrainingResult()

        print('Starting Training...')
        for i in range(iterations):
            print('Iteration {} of {}'.format(i, iterations))

            train_err = 0.0
            num_train_batches = 0
            for batch in _iterate_batch(train_inputs, train_targets, batch_size, True):
                inputs, targets = batch
                train_err += train_func(inputs, targets)
                num_train_batches += 1


            if val_inputs is not None:
                val_err = 0.0
                val_acc = 0.0
                num_val_batches = 0
                for batch in _iterate_batch(val_inputs, val_targets, batch_size, False):
                    inputs, targets = batch
                    err, acc = val_func(inputs, targets)
                    val_err += err
                    val_acc += acc
                    num_val_batches += 1

            training_loss = train_err / num_train_batches
            ret.training_losses.append(training_loss)

            print('\ttraining loss:\t\t{:.6f}'.format(training_loss))

            if val_inputs is not None:
                validation_loss = val_err / num_val_batches
                validation_accuracy = (val_acc / num_val_batches) * 100.0

                ret.validation_losses.append(validation_loss)
                ret.validation_accuracies.append(validation_accuracy)

                print('\tvalidation loss:\t\t{:.6f}'.format(validation_loss))
                print('\tvalidation accuracy:\t\t{:.2f}'.format(validation_accuracy))

        test_err = 0.0
        test_acc = 0.0
        num_test_batches = 0
        for batch in _iterate_batch(test_inputs, test_targets, batch_size, False):
            inputs, targets = batch
            err, acc = val_func(inputs, targets)
            test_err += err
            test_acc += acc
            num_test_batches += 1 

        test_loss = test_err / num_test_batches
        test_accuracy = (test_acc / num_test_batches) * 100.0

        ret.test_loss = test_loss
        ret.test_accuracy = test_accuracy

        print('\n===== Training Results =====')
        print('\ttest loss:\t\t{:.6f}'.format(test_loss))
        print('\ttest accuracy:\t\t{:.2f}'.format(test_accuracy))

        return ret
