import chainer.functions as cf
import chainer.links as cl
import chainer.reporter


class ResNet18(chainer.Chain):
    def __init__(self, dim_in=4, dim_out=512, use_bn=True):
        super(ResNet18, self).__init__()
        self.dim_in = dim_in
        self.dim_out = dim_out

        with self.init_scope():
            init = chainer.initializers.HeNormal()
            if use_bn:
                Normalization = cl.BatchNormalization
                no_bias = True

            dim_h = 64
            self.conv_in = cl.Convolution2D(dim_in, dim_h * 1, 7, stride=2, pad=3, initialW=init, nobias=no_bias)
            self.conv1_1_1 = cl.Convolution2D(dim_h * 1, dim_h * 1, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.conv1_1_2 = cl.Convolution2D(dim_h * 1, dim_h * 1, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.conv1_2_1 = cl.Convolution2D(dim_h * 1, dim_h * 1, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.conv1_2_2 = cl.Convolution2D(dim_h * 1, dim_h * 1, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.conv2_1_1 = cl.Convolution2D(dim_h * 1, dim_h * 2, 3, stride=2, pad=1, initialW=init, nobias=no_bias)
            self.conv2_1_2 = cl.Convolution2D(dim_h * 2, dim_h * 2, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.conv2_1_3 = cl.Convolution2D(dim_h * 1, dim_h * 2, 1, stride=2, pad=0, initialW=init, nobias=no_bias)
            self.conv2_2_1 = cl.Convolution2D(dim_h * 2, dim_h * 2, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.conv2_2_2 = cl.Convolution2D(dim_h * 2, dim_h * 2, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.conv3_1_1 = cl.Convolution2D(dim_h * 2, dim_h * 4, 3, stride=2, pad=1, initialW=init, nobias=no_bias)
            self.conv3_1_2 = cl.Convolution2D(dim_h * 4, dim_h * 4, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.conv3_1_3 = cl.Convolution2D(dim_h * 2, dim_h * 4, 1, stride=2, pad=0, initialW=init, nobias=no_bias)
            self.conv3_2_1 = cl.Convolution2D(dim_h * 4, dim_h * 4, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.conv3_2_2 = cl.Convolution2D(dim_h * 4, dim_h * 4, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.conv4_1_1 = cl.Convolution2D(dim_h * 4, dim_h * 8, 3, stride=2, pad=1, initialW=init, nobias=no_bias)
            self.conv4_1_2 = cl.Convolution2D(dim_h * 8, dim_h * 8, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.conv4_1_3 = cl.Convolution2D(dim_h * 4, dim_h * 8, 1, stride=2, pad=0, initialW=init, nobias=no_bias)
            self.conv4_2_1 = cl.Convolution2D(dim_h * 8, dim_h * 8, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.conv4_2_2 = cl.Convolution2D(dim_h * 8, dim_h * 8, 3, stride=1, pad=1, initialW=init, nobias=no_bias)
            self.linear_out = cl.Linear(dim_h * 8 * 7 * 7, dim_out)

            self.linear_in_bn = Normalization(dim_h * 1)
            self.conv_1_1_2_bn = Normalization(dim_h * 1)
            self.conv_1_2_1_bn = Normalization(dim_h * 1)
            self.conv_1_2_2_bn = Normalization(dim_h * 1)
            self.conv_2_1_1_bn = Normalization(dim_h * 1)
            self.conv_2_1_2_bn = Normalization(dim_h * 2)
            self.conv_2_2_1_bn = Normalization(dim_h * 2)
            self.conv_2_2_2_bn = Normalization(dim_h * 2)
            self.conv_3_1_1_bn = Normalization(dim_h * 2)
            self.conv_3_1_2_bn = Normalization(dim_h * 4)
            self.conv_3_2_1_bn = Normalization(dim_h * 4)
            self.conv_3_2_2_bn = Normalization(dim_h * 4)
            self.conv_4_1_1_bn = Normalization(dim_h * 4)
            self.conv_4_1_2_bn = Normalization(dim_h * 8)
            self.conv_4_2_1_bn = Normalization(dim_h * 8)
            self.conv_4_2_2_bn = Normalization(dim_h * 8)
            self.linear_out_bn = Normalization(dim_h * 8)

    def __call__(self, x):
        # [224 -> 112]
        h = cf.relu(self.linear_in_bn(self.conv_in(x)))
        h = cf.max_pooling_2d(h, ksize=3, stride=2, pad=0)

        # [112 -> 56]
        h1 = self.conv1_1_1(h)
        h1 = self.conv1_1_2(cf.relu(self.conv_1_1_2_bn(h1)))
        h = h + h1
        h1 = self.conv1_2_1(cf.relu(self.conv_1_2_1_bn(h)))
        h1 = self.conv1_2_2(cf.relu(self.conv_1_2_2_bn(h1)))
        h = h + h1

        # [56 -> 28]
        h1 = self.conv2_1_1(cf.relu(self.conv_2_1_1_bn(h)))
        h1 = self.conv2_1_2(cf.relu(self.conv_2_1_2_bn(h1)))
        h2 = self.conv2_1_3(h)
        h = h1 + h2
        h1 = self.conv2_2_1(cf.relu(self.conv_2_2_1_bn(h)))
        h1 = self.conv2_2_2(cf.relu(self.conv_2_2_2_bn(h1)))
        h = h + h1

        # [28 -> 14]
        h1 = self.conv3_1_1(cf.relu(self.conv_3_1_1_bn(h)))
        h1 = self.conv3_1_2(cf.relu(self.conv_3_1_2_bn(h1)))
        h2 = self.conv3_1_3(h)
        h = h1 + h2
        h1 = self.conv3_2_1(cf.relu(self.conv_3_2_1_bn(h)))
        h1 = self.conv3_2_2(cf.relu(self.conv_3_2_2_bn(h1)))
        h = h + h1

        # [14 -> 7]
        h1 = self.conv4_1_1(cf.relu(self.conv_4_1_1_bn(h)))
        h1 = self.conv4_1_2(cf.relu(self.conv_4_1_2_bn(h1)))
        h2 = self.conv4_1_3(h)
        h = h1 + h2
        h1 = self.conv4_2_1(cf.relu(self.conv_4_2_1_bn(h)))
        h1 = self.conv4_2_2(cf.relu(self.conv_4_2_2_bn(h1)))
        h = h + h1

        # [7 -> 1]
        h = cf.relu(self.linear_out_bn(h))
        h = self.linear_out(h)

        return h


def get_encoder(encoder_name, dim_in, dim_out):
    if encoder_name == 'resnet18':
        return ResNet18(dim_in, dim_out)
