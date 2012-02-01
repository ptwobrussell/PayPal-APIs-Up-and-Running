# The Product class provides product details. 
# A more flexible product line could be managed in a database

class Product(object):

  @staticmethod
  def getProduct():

    return {'price' : 4.99, 'quantity' : 50, 'units' : 'login tokens'}
