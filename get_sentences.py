from lxml import etree
import argparse

from ccg2jiggxml import read_abc

def main():
    parser = argparse.ArgumentParser('')
    parser.add_argument('FILE')
    parser.add_argument('-i',
                        '--skip-ill-formed',
                        action='store_true',
                        help='skip trees that contain a node whose arity > 2')
    parser.add_argument('-d',
                        '--drop-text',
                        action='store_true',
                        help='don\'t contain raw sentences in XML (useful for debugging)')
    args = parser.parse_args()

    trees = read_abc(args.FILE,
                     skip_ill_formed=args.skip_ill_formed)
    output_str = ''
    for t in trees:
        sentence = ' '.join(t.tokens) + '.#END#'
        output_str = output_str + sentence
    print(output_str)
    # print(' '.join(t.tokens))

if __name__ == '__main__':
    main()        
