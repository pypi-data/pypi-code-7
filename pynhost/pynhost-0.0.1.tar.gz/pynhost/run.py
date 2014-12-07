import time
import utilities
import grammarhandler

def main():
    m = grammarhandler.GrammarHandler()
    m.load_grammars()
    last_action = []
    add_space = False
    while True:
        lines = utilities.get_buffer_lines()
        time.sleep(.2)
        for line in lines:
            result = {'remaining words': line.split(' ')}
            results = []
            last_action = []
            while result['remaining words']:
                remaining_placeholder = result['remaining words']
                result = m.get_matching_rule(result['remaining words'])
                if result['rule'] is not None:
                    print(result)
                    result['rule'].func(result['new words'])
                    last_action.append((result['rule'].func, result['new words']))
                else:
                    utilities.transcribe_line(list(remaining_placeholder[0]),
                        len(remaining_placeholder) != 1)
                    last_action.append(remaining_placeholder[0])
                    result['remaining words'] = remaining_placeholder[1:]

if __name__ == '__main__':
    main()
