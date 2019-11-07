import tensorflow as tf
class Fs_net():
	def __init__(self, x, y):
		self.embedding_dim = 128
		self.hidden_dim = 128
		self.n_neurons = 128
		self.n_layers = 1
		self.n_steps = 22
		self.n_inputs = 128
		self.n_outputs = 11
		# self.X = tf.placeholder(tf.float32, [None, self.n_steps, self.n_inputs])
		# self.Y = tf.placeholder(tf.float32, [None,1])	
		self.X = x
		self.Y = y
		self.alpha = 1	

	def bi_lstm(self):
	    # 顺时间循环层的记忆细胞，堆叠了两层
	    lstm_fw1 = tf.nn.rnn_cell.LSTMCell(num_units=n_neurons)
	    lstm_fw2 = tf.nn.rnn_cell.LSTMCell(num_units=n_neurons)
	    lstm_forward = tf.nn.rnn_cell.MultiRNNCell(cells=[lstm_fw1,lstm_fw2])
	    # 拟时间循环层的记忆细胞，堆叠了两层
	    lstm_bc1 = tf.nn.rnn_cell.LSTMCell(num_units=n_neurons)
	    lstm_bc2 = tf.nn.rnn_cell.LSTMCell(num_units=n_neurons)
	    lstm_backward = tf.nn.rnn_cell.MultiRNNCell(cells=[lstm_bc1,lstm_bc2])
	    # 计算输出和隐状态
	    outputs,states=tf.nn.bidirectional_dynamic_rnn(cell_fw=lstm_forward, cell_bw=lstm_backward,inputs=self.X,dtype=tf.float32)
	    # 取到顺时间循环层和拟时间循环层的最后一个隐状态
	    state_forward = states[0][-1][-1]
	    state_backward = states[1][-1][-1]
	    # 把两个隐状态拼接起来。
	    return state_forward+state_backward

	def bi_gru(self,x):
	    gru_forward = tf.nn.rnn_cell.GRUCell(num_units=n_neurons)
	    gru_backward = tf.nn.rnn_cell.GRUCell(num_units=n_neurons)
	    outputs,states=tf.nn.bidirectional_dynamic_rnn(cell_fw=gru_forward, cell_bw=gru_backward,inputs=x,dtype=tf.float32)
	    return states

	def bi_gru_2(self,x):
	    # 顺时间循环层的记忆细胞，堆叠了两层
	    gru_fw1 = tf.nn.rnn_cell.GRUCell(num_units=n_neurons)
	    gru_fw2 = tf.nn.rnn_cell.GRUCell(num_units=n_neurons)
	    gru_forward = tf.nn.rnn_cell.MultiRNNCell(cells=[gru_fw1,gru_fw2])
	    # 拟时间循环层的记忆细胞，堆叠了两层
	    gru_bc1 = tf.nn.rnn_cell.GRUCell(num_units=n_neurons)
	    gru_bc2 = tf.nn.rnn_cell.GRUCell(num_units=n_neurons)
	    gru_backward = tf.nn.rnn_cell.MultiRNNCell(cells=[gru_bc1,gru_bc2])
	    # 计算输出和隐状态
	    outputs,states=tf.nn.bidirectional_dynamic_rnn(cell_fw=gru_forward, cell_bw=gru_backward,inputs=x,dtype=tf.float32)
	    # 取到顺时间循环层和拟时间循环层的最后一个隐状态
	    # state_forward = states[0][-1]
	    # state_backward = states[1][-1]
	    # 把两个隐状态拼接起来。
	    # return state_forward+state_backward
	    return states

	def fs_net(self):
		#add embedding 
		encoder_output = self.bi_gru(self.X)
		encoder_feats = tf.concate([encoder_output[0][-1], encoder_output[1][-1]],axis=-1)
		decoder_output = self.bi_gru(encoder_feats)
		decoder_feats = tf.concate([decoder_output[0][-1], decoder_output[1][-1]],axis=-1)
		element_wise_product = encoder_feats * decoder_feats
		element_wise_absolute = tf.abs(encoder_feats,decoder_feats)
		cls_feats = tf.concat([encoder_feats, decoder_feats, element_wise_product, element_wise_absolute],axis = -1)
		cls_dense_1 = tf.layers.dense(inputs=cls_feats,units= self.n_neurons,activation=tf.nn.selu,kernel_regularizer=tf.contrib.layers.l2_regularizer(0.003))
		cls_dense_2 = tf.layers.dense(inputs=cls_dense1,units=self.n_outputs,activation=tf.nn.relu,kernel_regularizer=tf.contrib.layers.l2_regularizer(0.003),name="softmax") 
		return cls_dense2, decoder_output

	def build_loss(self):
		logits, ae_outputs = self.fs_net()
		cls_entropy = tf.nn.sparse_softmax_cross_entrop_with_logits(labers=y, logits=logits)
		cls_loss = tf.redice_mean(cls_entropy, name="cls_loss")
		ae_loss = 0
		total_loss = cls_loss + self.alpha * ae_loss
		return total_loss


