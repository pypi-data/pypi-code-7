from django.utils.functional import SimpleLazyObject

obj = SimpleLazyObject(lambda: 'asdfasdfasdf')
str(obj)
print('*'*80)
print('*'*80)
print('*'*80)

str(obj)



