import matplotlib.pyplot as plt


x = [1,2,3,4,5]
y1 = [1,2,3,4,5]
y2 = [2,3,0,5,6]

def sampleplot(x,y1,y2):
	plt.gca().set_color_cycle(['red', 'green'])
        plt.plot(x, y1)
        plt.plot(x, y2)
        plt.legend(['market', 'aapl'], loc='upper left')
        plt.show()

if __name__ == '__main__':
	sampleplot(x,y1,y2)

