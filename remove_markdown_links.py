
def remove_markdown_links(text_string):
    def remove_single_link(start, end):
        return text_string[:start] + text_string[end:]

    first_square = -1
    first_round = -1
    result = []
    indicies_squares = []
    indicies_rounds = []
    square_found = False
    # first find all the indicies where the links are
    for i in range(len(text_string)):
        char = text_string[i]
        if char == '[':
            first_square = i
        elif char == ']':
            if first_square > -1:
                if i + 1 < len(text_string) and text_string[i + 1] == '(' :
                    indicies_squares.append((first_square, i))
                    first_square = -1
                    square_found = True
        elif square_found and char == '(' : 
            first_round = i
        elif square_found and char == ')':
                indicies_rounds.append((first_round, i))
                first_round = -1
                square_found = False
    if len(indicies_squares) != len(indicies_rounds) :
        raise ValueError("len(indicies_squares) != len(indicies_rounds)")

    start = 0
    final_string = ""    
    # remove with squares 
    for i in range(len(indicies_squares)):
        #[text should stay in between]
        first, second = indicies_squares[i]
        final_string += text_string[start:first]
        start = first + 1
        final_string += text_string[start:second]
        start = second + 1 
        # (should remove everything)
        first, second = indicies_rounds[i]
        final_string += text_string[start:first]
        start = second + 1
    final_string += text_string[start:]
    return final_string

def unbold(text):
    without = text.replace('**', '')
    return without

import debugpy
import argparse
def main(args):
    if args != None:
        if args.debug:
            port = 5678        
            print(f"Waiting debugger at {port}")
            debugpy.listen(5678)
            debugpy.wait_for_client()

    # Example usage:
    text = "[](http://example.com)Here is a [link](http://example.com) to an example site.[](http://example.com)"
    cleaned_text = remove_markdown_links(text)
    cleaned_text_test = cleaned_text == "Here is a link to an example site."
    if not cleaned_text_test:
        print(f"cleaned_text_test failed:  {cleaned_text}")

    # only link 
    text = "[](http://example.com)"
    cleaned_text = remove_markdown_links(text)
    empty_link_test = cleaned_text == ""
    if not empty_link_test:
        print(f"empty_link_test failed:  {cleaned_text}")

    text = "[Should do nothing]"
    cleaned_text = remove_markdown_links(text)
    nothing_test = cleaned_text == "[Should do nothing]"
    if not nothing_test:
        print(f"nothing_test failed:  {cleaned_text}")

    # test bold removal 
    text = "**this is a bold text**"
    cleaned_text = unbold(text)
    bold_test = cleaned_text == "this is a bold text" 
    if not bold_test:
        print(f"bold test failed: {cleaned_text}") 
    
    if cleaned_text_test and empty_link_test and nothing_test:
        print("Successs")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="An example Python script")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--verbose", action="store_true", help="Tells some statistics")
    args = parser.parse_args()
    # Call the main function with the args parameter set
    main(args)
