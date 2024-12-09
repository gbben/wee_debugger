import sys
import linecache
import inspect
from typing import Any, Optional

class SimpleDebugger:
    def __init__(self):
        self.step_mode = False
        self.continue_mode = False
        self.current_frame: inspect.FrameInfo | None = None
        self.commands = {
            'h': self._help,
            'n': self._step,
            'p': self._print_variable,
            'l': self._list_source,
            'c': self._continue,
            'v': self._list_variables,
            'q': self._quit
        }
    
    def _help(self, arg: str) -> None:
        """Show available commands."""
        print("\nAvailable commands:")
        print("h: Show this help")
        print("n: Step to next line")
        print("p <var>: Print variable value")
        print("l: List source code around current line")
        print("c: Continue execution")
        print("v: Show all local variables")
        print("q: Quit debugging")
        
    def _step(self, arg: str) -> None:
        """Step to next line."""
        self.step_mode = True
        
    def _continue(self, arg: str) -> None:
        """Continue execution until next breakpoint or end."""
        self.continue_mode = True
        
    def _print_variable(self, arg: str) -> None:
        """Print value of specified variable."""
        if not arg:
            print("Usage: p <variable_name>")
            return
            
        try:
            # * Get variable from local or global scope
            frame = self.current_frame.frame
            value = frame.f_locals.get(arg, frame.f_globals.get(arg, '<not found>'))
            print(f"{arg} = {value}")
        except Exception as e:
            print(f"Error accessing variable: {e}")
            
    def _list_variables(self, arg: str) -> None:
        """List all local variables and their values."""
        if self.current_frame:
            locals_dict = self.current_frame.frame.f_locals
            for name, value in locals_dict.items():
                print(f"{name} = {value}")
                
    def _list_source(self, arg: str) -> None:
        """Show source code around current line."""
        if not self.current_frame:
            return
            
        frame = self.current_frame.frame
        filename = frame.f_code.co_filename
        current_line = frame.f_lineno
        
        # * Show 5 lines before and after current line
        start_line = max(current_line - 5, 1)
        end_line = current_line + 5
        
        print(f"\nSource code around line {current_line}:")
        for line_num in range(start_line, end_line + 1):
            line = linecache.getline(filename, line_num).rstrip()
            marker = '-->' if line_num == current_line else '   '
            print(f"{marker} {line_num:4d} {line}")
            
    def _quit(self, arg: str) -> None:
        """Quit the debugger."""
        sys.exit(0)
        
    def trace_function(self, frame, event: str, arg: Any) -> Optional[callable]:
        """Main trace function called by Python's trace mechanism."""
        if event == 'line':
            # * Convert frame to FrameInfo object for easier access
            self.current_frame = inspect.getframeinfo(frame)
            
            # * If we're not in continue mode, show current line and prompt
            if not self.continue_mode:
                self._show_current_line()
                self._prompt_command()
                
            # * Reset step mode after each step
            self.step_mode = False
            
        return self.trace_function if not self.continue_mode else None
        
    def _show_current_line(self) -> None:
        """Show the current line being executed."""
        if self.current_frame:
            filename = self.current_frame.filename
            lineno = self.current_frame.lineno
            line = linecache.getline(filename, lineno).strip()
            print(f"\nAt {filename}:{lineno}")
            print(f"--> {line}")
            
    def _prompt_command(self) -> None:
        """Prompt for and handle debugger commands."""
        while True:
            try:
                cmd = input("(SimpleDebugger) ")
                if not cmd:
                    continue
                    
                command, *args = cmd.split(maxsplit=1)
                arg = args[0] if args else ''
                
                if command in self.commands:
                    self.commands[command](arg)
                    if command in ['n', 'c']:  # * Commands that continue execution
                        break
                else:
                    print(f"Unknown command: {command}")
                    self._help('')
            except KeyboardInterrupt:
                print("\nUse 'q' to quit")
            except Exception as e:
                print(f"Error: {e}")
                
    def start(self) -> None:
        """Start the debugger."""
        sys.settrace(self.trace_function)

# ! Example usage
def example_function(n):
    x = 1
    y = 2
    result = x + y + n
    for i in range(n):
        result += i
    return result

if __name__ == "__main__":
    debugger = SimpleDebugger()
    debugger.start()
    
    # Run some code under the debugger
    result = example_function(3)
    print(f"Final result: {result}")