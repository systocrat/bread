import re
import socket
import six

def frozen(func):
	def frozenWrapper(*args, **kwargs):
		return lambda x: func(x, *args, **kwargs)
	return frozenWrapper


class ValidationException(Exception):
	pass


@frozen
def ValidateInteger(x):
	try:
		x = int(x)
	except ValueError:
		raise ValidationException('Not an integer.')
	return x


@frozen
def ValidateFloat(x):
	try:
		x = float(x)
	except ValueError:
		raise ValidationException('Not a floating point value.')
	return x


@frozen
def ValidateExtension(x, extensions):
	def is_allowed(filename):
		return '.' in filename and filename.rsplit('.', 1)[1] in extensions
	if not is_allowed(x.filename):
		raise ValidationException('Invalid file extension.')
	return x


@frozen
def ValidateLength(x, minimum=None, maximum=None):
	xlen = len(x)
	if minimum is not None:
		if xlen < minimum:
			raise ValidationException('Length must be above {0}.'.format(minimum))
	if maximum is not None:
		if xlen > maximum:
			raise ValidationException('Length must be below {0}'.format(maximum))
	return x


@frozen
def ValidateCharset(x, charset):
	for i, c in enumerate(x):
		if not c in charset:
			raise ValidationException('Invalid character at position {0}: {1}'.format(i, c))
	return x

email_regex = re.compile(r'[^@\s-]+@[^@\s-]+\.[^@\s-]+')


@frozen
def ValidateEmail(x, validateDomain=False):
	if email_regex.match(x) is None:
		raise ValidationException('Invalid email.')
	if validateDomain:
		try:
			socket.getaddrinfo(x.split('@')[1], None)
		except:
			raise ValidationException('Invalid email.')
	return x


@frozen
def ValidateURL(x, validHosts=None, validSchemes=('http', 'https'), validateDomain=False):
	result = six.moves.urllib.parse.urlparse(x)
	if not result.netloc:
		raise ValidationException('Invalid URL.')
	if validHosts and result.netloc not in validHosts:
		raise ValidationException('Invalid URL.')
	if validSchemes and result.scheme not in validSchemes:
		raise ValidationException('Invalid URL.')
	if validateDomain:
		try:
			socket.getaddrinfo(result.netloc, None)
		except:
			raise ValidationException('Invalid URL.')
	return x


@frozen
def ValidateOption(x, options=list()):
	if not x in options:
		raise ValidationException('Invalid option.')
	return x


@frozen
def ValidateRange(x, rtype=int, minimum=None, maximum=None):
	val = rtype(x)
	if minimum is not None:
		if val < minimum:
			raise ValidationException('Number must be above {0}'.format(minimum))
	if maximum is not None:
		if val > maximum:
			raise ValidationException('Number must be below {0}'.format(maximum))
	return x


@frozen
def ValidateList(x, validator):
	for i, val in enumerate(x):
		try:
			validator(val)
		except ValidationException as ex:
			raise ValidationException('Item {0} of list failed validation: {1}'.format(i, ex.message))
	return x