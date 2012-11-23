import cmd
import Types
import Search
import Parser
import traceback
import sympy

class Prolog_Plus(cmd.Cmd):
    """Simple command processor example."""
    prompt = "Prolog+>>"
    CE = set()

    def do_dump(self, line):
        for item in self.CE:
            print item

    def default(self, line):
        if len(line) == 0:
            return

        if line[-2:] == '?n':
            print Search.search_expr(self.CE, sympy.Symbol(line[:-2]))
            return
        elif line[-1] == '?':
            print Search.search(self.CE, Parser._parse_pred(line[:-1]))
            return

        try:
            self.CE.update(Parser._parse(line))
            print 'Accepted'
        except:
            print traceback.format_exc()

    def do_EOF(self, line):
        print 'EOF'
        return True

if __name__ == '__main__':
    print "Prolog+ By Colin Rice"
    print "-" * 40
    Prolog_Plus().cmdloop()
