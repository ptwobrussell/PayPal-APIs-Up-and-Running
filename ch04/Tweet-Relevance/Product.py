# The Product class provides product details. 
# A more flexible product line could be managed in a database

class Product(object):

  @staticmethod
  def getProduct():

    return {'price' : 9.99, 'quantity' : 30, 'units' : 'days'}
