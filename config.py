import argparse
import inspect
import json
import sys
from ast import literal_eval
import six

from validation import ValidationException


class ConfigOption(object):
	def __init__(self, default=None, description='', validators=None):
		self.default = default
		self.description = description
		self.type = type
		self.validators = validators or list()


class Configurator(object):
	def __init__(self, file):
		self._file = file

	def loadConfig(self):
		try:
			with open(self._file, 'r') as f:
				obj = json.load(f)
			return obj
		except:
			return dict()

	def applyConfig(self):
		obj = self.loadConfig()
		for key, val in six.iteritems(obj):
			setattr(sys.modules[__name__], key, val)

	def saveConfig(self, obj):
		with open(self._file, 'w') as f:
			json.dump(obj, f)

	def main(self):
		parser = argparse.ArgumentParser(description='Configure your application.')

		choices = ['all']

		options = dict()

		for (name, value) in inspect.getmembers(sys.modules[__name__], lambda x: isinstance(x, ConfigOption)):
			options[name] = value
			choices.append(name)

		parser.add_argument('option', choices=choices, help='The configuration option to configure.')

		args = parser.parse_args()
		option = args.option

		if option == 'all':
			cfg = self.loadConfig()
			for name, configObject in six.iteritems(options):
				try:
					data = Configurator._queryUser(name, configObject, cfg[name] if cfg.has_key(name) else configObject.default)
					cfg[name] = data
				except Exception as ex:
					six.print_('Failed to configure {0}: {1}'.format(name, repr(ex)))
			six.print_('Saving configuration')
			self.saveConfig(cfg)

		elif option == 'help':
			six.print_('Not implemented.')
		else:
			configObject = getattr(sys.modules[__name__], option)
			cfg = self.loadConfig()

			try:
				data = Configurator._queryUser(option, configObject, cfg[option] if cfg.has_key(option) else configObject.default)
				cfg[option] = data
			except Exception as ex:
				six.print_('Failed to configure {0}: {1}'.format(option, repr(ex)))

			six.print_('Saving configuration')
			self.saveConfig(cfg)

	@staticmethod
	def _queryUser(name, configObject, default):
		data = six.moves.input('ConfigOption[{name}, {default}]: '.format(name=name, default=default))
		try:
			data = literal_eval(data)
		except:
			data = str(data)
		if data == 'null':
			data = None
		elif isinstance(data, six.string_types) and len(data) == 0:
			data = default

		for val in configObject.validators:
			try:
				data = val(data)
			except ValidationException as ex:
				six.print_('Failed to validate {0}: {1}'.format(name, ex.message))
				raise Exception('Failed to validate.')
		return data

localPort = ConfigOption(description='The local port to forward')
forwards = ConfigOption(description='The forwards for breadproxy in a dictionary in the format of {\'protocolName\': \'clientString\'}')

configurator = Configurator('breadproxy.json')

if __name__ == '__main__':
	configurator.main()
else:
	configurator.applyConfig()
