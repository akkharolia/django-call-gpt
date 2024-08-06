tools = [
  {
    'type': 'function',
    'function': {
      'name': 'save_customer_details',
      'say': '',
      'description': 'Save the user name and phone number to the database.',
      'parameters': {
        'type': 'object',
        'properties': {
          'full_name': {
            'type': 'string',
            'description': 'The full name of the user',
          },
          'call_sid': {
            'type': 'string',
            'description': 'The active twilio call id.',
          }
        },
        'required': ['full_name', 'call_sid'],
      },
      'returns': {
        'type': 'object',
        'properties': {
          'status': {
            'type': 'string',
            'description': 'Whether or not the customer detailed were saved successfully.'
          },
        }
      }
    },
  },
  {
    'type': 'function',
    'function': {
      'name': 'appointment_booking',
      'say': '',
      'description': 'Save the appointment date/time to the database.',
      'parameters': {
        'type': 'object',
        'properties': {
          'day': {
            'type': 'string',
            'description': 'The day of the appointment',
          },
          'time': {
            'type': 'string',
            'description': 'The time of the appointment in 12 hours format.',
          },
          'call_sid': {
            'type': 'string',
            'description': 'The active twilio call id.',
          }
        },
        'required': ['day', 'time', 'call_sid'],
      },
      'returns': {
        'type': 'object',
        'properties': {
          'status': {
            'type': 'string',
            'description': 'Whether or not the appointment detailed were saved successfully.'
          },
        }
      }
    },
  },
  # {
  #     'type':'function',
  #     'function': {
  #     'name': 'end_call',
  #     'say': '',
  #     'description': 'End the ongoing call.',
  #     'parameters': {
  #       'type': 'object',
  #       'properties': {
  #         'call_sid': {
  #           'type': 'string',
  #           'description': 'The active twilio call id.',
  #         }
  #       },
  #       'required': ['call_sid'],
  #     },
  #     'returns': {
  #       'type': 'object',
  #       'properties': {
  #         'status': {
  #           'type': 'string',
  #           'description': 'End call message.'
  #         },
  #       }
  #     }
  #   },
  # }
]