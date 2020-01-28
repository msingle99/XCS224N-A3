class PartialParse(object):
    def __init__(self, sentence):
        """Initializes this partial parse.

        Your code should initialize the following fields:
            self.stack: The current stack represented as a list with the top of the stack as the
                        last element of the list.
            self.buffer: The current buffer represented as a list with the first item on the
                         buffer as the first item of the list
            self.dependencies: The list of dependencies produced so far. Represented as a list of
                    tuples where each tuple is of the form (head, dependent).
                    Order for this list doesn't matter.

        The root token should be represented with the string "ROOT"

        Args:
            sentence: The sentence to be parsed as a list of words.
                      Your code should not modify the sentence.
        """
        # The sentence being parsed is kept for bookkeeping purposes. Do not use it in your code.
        self.sentence = sentence

        ### YOUR CODE HERE (3 Lines)
        self.stack = ['ROOT']       # stack.append('word') appends item 'word' to list called 'stack'
                                    # del stack[-1] removes the last (rightmost) element of the list called 'stack'
        self.buffer = sentence.copy()      # del buffer[0] will remove the first (leftmost) element from list 'buffer'
        self.dependencies = []      # dep.append(('a','b')) appends tuple ('a','b') to list called 'dep'
        ### END YOUR CODE

    def parse_step(self, transition):
        """Performs a single parse step by applying the given transition to this partial parse

        Args:
            transition: A string that equals "S", "LA", or "RA" representing the shift, left-arc,
                        and right-arc transitions. You can assume the provided transition is a legal
                        transition.
        """
        ### YOUR CODE HERE (~7-10 Lines)
        ### TODO:
        ###     Implement a single parsing step, i.e. the logic for the following as
        ###     described in the pdf handout:
        ###         1. Shift: removes the first word from the buffer and pushes it onto the stack
        ###         2. Left Arc: marks the second (second most recently added) item on the stack as a dependent
        ###            of the first item and removes the second item from the stack.
        ###         3. Right Arc: marks the first (most recently added) item on the stack as a depedent of the 
        ###            second item and removes the first item from the stack.
        if transition=="S":
            self.stack.append(self.buffer[0])
            del self.buffer[0]
        elif transition=="LA":
            self.dependencies.append((self.stack[-1], self.stack[-2]))
            del self.stack[-2]
        elif transition=="RA":
            self.dependencies.append((self.stack[-2], self.stack[-1]))
            del self.stack[-1]
        ### END YOUR CODE

    def parse(self, transitions):
        """Applies the provided transitions to this PartialParse

        Args:
            transitions: The list of transitions in the order they should be applied
        Returns:
            dependencies: The list of dependencies produced when parsing the sentence. Represented
                          as a list of tuples where each tuple is of the form (head, dependent)
        """
        for transition in transitions:
            self.parse_step(transition)
        return self.dependencies


def minibatch_parse(sentences, model, batch_size):
    """Parses a list of sentences in minibatches using a model.

    Args:
        sentences: A list of sentences to be parsed (each sentence is a list of words)
        model: The model that makes parsing decisions. It is assumed to have a function
               model.predict(partial_parses) that takes in a list of PartialParses as input and
               returns a list of transitions predicted for each parse. That is, after calling
                   transitions = model.predict(partial_parses)
               transitions[i] will be the next transition to apply to partial_parses[i].
        batch_size: The number of PartialParses to include in each minibatch
    Returns:
        dependencies: A list where each element is the dependencies list for a parsed sentence.
                      Ordering should be the same as in sentences (i.e., dependencies[i] should
                      contain the parse for sentences[i]).
    """

    ### YOUR CODE HERE (~8-10 Lines)
    ### TODO:
    ###     Implement the minibatch parse algorithm as described in the pdf handout
    ###
    ###     Note: A shallow copy (as denoted in the PDF) can be made with the "=" sign in python, e.g.
    ###                 unfinished_parses = partial_parses[:].
    ###             Here `unfinished_parses` is a shallow copy of `partial_parses`.
    ###             In Python, a shallow copied list like `unfinished_parses` does not contain new instances
    ###             of the object stored in `partial_parses`. Rather both lists refer to the same objects.
    ###             In our case, `partial_parses` contains a list of partial parses. `unfinished_parses`
    ###             contains references to the same objects. Thus, you should NOT use the `del` operator
    ###             to remove objects from the `unfinished_parses` list. This will free the underlying memory that
    ###             is being accessed by `partial_parses` and may cause your code to crash.

    ### PartialParse.minibatch_parse() receives a list of sentences top parse, a reference to a model object with a predict() method to predict the next transition, and a batch_size
    ### It initializes two lists: partial_parses, a list of PartialParse objects; and unfinished_parses, a shallow copy of partial_parses.
    ### •	Instructions say = makes a shallow copy, but I don’t think that’s right
    ### •	Use list.copy or list[:] to make a shallow copy.
    ### 	a = [1,2]
    ###     o	b=a.copy() or b=a[:]
    ###         •	Then, elementwise changes to b WILL affect the corresponding element of a, but “list-level” operations on b will not affect a
    ###     o	b.append(3)		- should not affect a
    ###     o	b[0].append(3)		- should affect a
#    sentences=[['this','is','sentence','one'],['this','is','sentence','two'],['this','is','sentence','three'],['this','is','sentence','four'],['this','is','sentence','five']]
#    BATCH_SIZE = 3
#    model = DummyModel()
    
    partial_parses = [PartialParse(s) for s in sentences]
    unfinished_parses = partial_parses.copy()
    
    ### Loop until all sentences are completely parsed
    while len(unfinished_parses) != 0:
        ### It selects a list of the first [batch_size] elements of unfinished_parses (“BATCH”), and sends that list to model.predict(), which will return a list of predicted transitions for each unfinished parse.
        if len(unfinished_parses) >= batch_size:
            batch = unfinished_parses[:batch_size]  
        else:
                batch = unfinished_parses 
        transitions = model.predict(batch)

    ### Apply transitions
        [batch[i].parse_step(transitions[i]) for i in range(len(batch))]   
    
    ### Iterate over BATCH, and remove those parses having empty buffer and stack size of 1 from the unfinished_parses list 
        for pp in reversed(range(len(batch))):
            if (len(batch[pp].stack)==1) & (len(batch[pp].buffer)==0):
                unfinished_parses.pop(pp) 
    
    ### Build a final list of dependency parses to return to the caller
    dependencies = [pp.dependencies for pp in partial_parses]

    ### END YOUR CODE

    return dependencies


def test_step(name, transition, stack, buf, deps,
              ex_stack, ex_buf, ex_deps):
    """Tests that a single parse step returns the expected output"""
    pp = PartialParse([])
    pp.stack, pp.buffer, pp.dependencies = stack, buf, deps

    pp.parse_step(transition)
    stack, buf, deps = (tuple(pp.stack), tuple(pp.buffer), tuple(sorted(pp.dependencies)))
    assert stack == ex_stack, \
        "{:} test resulted in stack {:}, expected {:}".format(name, stack, ex_stack)
    assert buf == ex_buf, \
        "{:} test resulted in buffer {:}, expected {:}".format(name, buf, ex_buf)
    assert deps == ex_deps, \
        "{:} test resulted in dependency list {:}, expected {:}".format(name, deps, ex_deps)
    print("{:} test passed!".format(name))


def test_parse_step():
    """Simple tests for the PartialParse.parse_step function
    Warning: these are not exhaustive
    """
    test_step("SHIFT", "S", ["ROOT", "the"], ["cat", "sat"], [],
              ("ROOT", "the", "cat"), ("sat",), ())
    test_step("LEFT-ARC", "LA", ["ROOT", "the", "cat"], ["sat"], [],
              ("ROOT", "cat",), ("sat",), (("cat", "the"),))
    test_step("RIGHT-ARC", "RA", ["ROOT", "run", "fast"], [], [],
              ("ROOT", "run",), (), (("run", "fast"),))


def test_parse():
    """Simple tests for the PartialParse.parse function
    Warning: these are not exhaustive
    """
    sentence = ["parse", "this", "sentence"]
    dependencies = PartialParse(sentence).parse(["S", "S", "S", "LA", "RA", "RA"])
    dependencies = tuple(sorted(dependencies))
    expected = (('ROOT', 'parse'), ('parse', 'sentence'), ('sentence', 'this'))
    assert dependencies == expected, \
        "parse test resulted in dependencies {:}, expected {:}".format(dependencies, expected)
    assert tuple(sentence) == ("parse", "this", "sentence"), \
        "parse test failed: the input sentence should not be modified"
    print("parse test passed!")


class DummyModel(object):
    """Dummy model for testing the minibatch_parse function
    First shifts everything onto the stack and then does exclusively right arcs if the first word of
    the sentence is "right", "left" if otherwise.
    """

    def predict(self, partial_parses):
        return [("RA" if pp.stack[1] is "right" else "LA") if len(pp.buffer) == 0 else "S"
                for pp in partial_parses]


def test_dependencies(name, deps, ex_deps):
    """Tests the provided dependencies match the expected dependencies"""
    deps = tuple(sorted(deps))
    assert deps == ex_deps, \
        "{:} test resulted in dependency list {:}, expected {:}".format(name, deps, ex_deps)


def test_minibatch_parse():
    """Simple tests for the minibatch_parse function
    Warning: these are not exhaustive
    """
    sentences = [["right", "arcs", "only"],
                 ["right", "arcs", "only", "again"],
                 ["left", "arcs", "only"],
                 ["left", "arcs", "only", "again"]]
    deps = minibatch_parse(sentences, DummyModel(), 2)
    test_dependencies("minibatch_parse", deps[0],
                      (('ROOT', 'right'), ('arcs', 'only'), ('right', 'arcs')))
    test_dependencies("minibatch_parse", deps[1],
                      (('ROOT', 'right'), ('arcs', 'only'), ('only', 'again'), ('right', 'arcs')))
    test_dependencies("minibatch_parse", deps[2],
                      (('only', 'ROOT'), ('only', 'arcs'), ('only', 'left')))
    test_dependencies("minibatch_parse", deps[3],
                      (('again', 'ROOT'), ('again', 'arcs'), ('again', 'left'), ('again', 'only')))
    print("minibatch_parse test passed!")


if __name__ == '__main__':
    test_parse_step()
    test_parse()
    test_minibatch_parse()
