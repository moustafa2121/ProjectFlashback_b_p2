import json, time

"""
decorator that delays view functions
simulates getting data from the API to test frontend functionality
"""
def delayResponse(timeMultiplier):
    def decorator(viewFunc):
        def wrapper(request, *args, **kwargs):
            delayTime = timeMultiplier * int(kwargs.get('stageNumber', 0))
            time.sleep(delayTime)
            response = viewFunc(request, *args, **kwargs)

            return response
        return wrapper
    return decorator


def testData():
    dataFile = open('napleon_test.json', 'r')
    data = json.load(dataFile)
    dataFile.close()
    print(type(data))
    return data

