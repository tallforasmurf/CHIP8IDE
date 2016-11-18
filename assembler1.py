__license__ = '''
 License (GPL-3.0) :
    This file is part of CHIP8IDE.

    CHIP8IDE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You can find a copy of the GNU General Public License in the file
    COPYING.TXT included in the distribution of this program, or see:
    <http://www.gnu.org/licenses/>.
'''
__version__ = "1.0.0"
__author__  = "David Cortesi"
__copyright__ = "Copyright 2016 David Cortesi"
__maintainer__ = "David Cortesi"
__email__ = "davecortesi@gmail.com"

'''

    CHIP-8 IDE ASSEMBLY PHASE ONE

This is a sub-module of the source.py module, which implements the source
editor window.

The code here implements the initial assembly syntax check, which is called
from the QSyntaxHighlighter attached to the edit document. Each time a line
is modified the Syntax Highlighter is called. It calls phase_one() in this
module to render that source line into a Statement object, which is stored in
the UserData field of the QTextBlock.

A number of errors are caught here and reported as two fields of the
Statement object. The user is notified by the editor when a statement is
invalid.

When the statement text is valid, the resulting Statement object has the info
needed to complete the assembly later, in the assemble() function of the
assemble2 module.

'''

'''
Define exported names.

This module exports just the phase_one function.
All other defined names are internal to the module.
'''
__all__ = [ 'phase_one' ]

'''
Import the Statement class
'''
from statement_class import Statement

'''
Import the register code numbers from the emulator.
'''

from chip8 import R as RCODES

'''

    Tokenization by Regular Expression

Refer to https://docs.python.org/dev/library/re.html#writing-a-tokenizer for
some insight into what's going on here. TL;DR: we set up a list of named
regular expressions to recognize all valid token forms that can occur.

Note the regexen are processed with the ignore-case flag, so capitalization
doesn't matter.

We use the pypi module regex which is faster and has more features than the
standard re. (Although no special regex features are used, so the standard
re module would work. Just not quite as fast. And we need to be fast, because
the regexes get exercised for EVERY FUCKING KEYSTROKE in the editor. Really.)

The regex for each specific directive or opcode needs to be fenced with
the \b word-break test. Otherwise we tend to recognize opcodes at the start
or end of innocent labels.
'''

import regex

'''
List of Directive opcodes. A search for these is the first item in the
tokenizer regex. It was important that they be first so that the ORG directive
would be recognized ahead of the search for the OR opcode -- however that
is no longer an issue since the insertion of the \b markers.
'''

directives = [
    r'\bDA\b',
    r'\bDB\b',
    r'\bDW\b',
    r'\bDS\b',
    r'\bEQU\b',
    r'=',
    r'\bORG\b',
    ]

'''
List of instruction opcodes. The search for the names in this list is the
second item in the tokenizer regex.
'''

opcodes = [
    r'\bADD\b',
    r'\bAND\b',
    r'\bCALL\b',
    r'\bCLS\b',
    r'\bDRAW\b',
    r'\bEXIT\b',
    r'\bHIGH\b',
    r'\bJP\b',
    r'\bLDC\b',
    r'\bLDH\b',
    r'\bLDM\b',
    r'\bLD\b',
    r'\bLOW\b',
    r'\bOR\b',
    r'\bRET\b',
    r'\bRND\b',
    r'\bSCD\b',
    r'\bSCL\b',
    r'\bSCR\b',
    r'\bSE\b',
    r'\bSHL\b',
    r'\bSHR\b',
    r'\bSKP\b',
    r'\bSKNP\b',
    r'\bSNE\b',
    r'\bSTD\b',
    r'\bSTM\b',
    r'\bSUBN\b',
    r'\bSUB\b',
    r'\bXOR\b'
    ]

'''
List of V-reg names. The search for these is third in the tokenizer.
'''

v_regs = [ r'\bv'+c+r'\b' for c in '0123456789ABCDEF' ]

'''

Define and name the legal tokens as (token-class-name, regex-to-match-it).

They must be listed from explicit to general, i.e. look for specific opcodes
before the more general WORD token.

Notes re the STRING token. It only recognizes the use of 'single' quotes; it
will not recognize double-quotes. It does recognize a null string (which will
be assembled as DS 0). The assembler doc says that to include a single quote,
double it: 'MA''AM'. In tokenizing, that just resolves to two string tokens,
STRING(MA) and STRING(AM). While processing tokens we note this and glue them
back together.
'''

token_specs = [
    ( 'LABEL',     r'^\s*[A-Z0-9_]+\s*\:' ), # Word: anchored to ^ is a label
    ( 'WHITE',     '\s+'                  ), # ignored whitespace
    ( 'DIRECTIVE', '|'.join( directives ) ), # directives
    ( 'OPCODE',    '|'.join( opcodes )    ), # known opcodes
    ( 'VREG',      '|'.join( v_regs )     ), # v regs
    ( 'IREG',      r'\bI\b'               ), # treat special regs specially
    ( 'KREG',      r'\bK\b'               ),
    ( 'DTREG',     r'\bDT\b'              ),
    ( 'DSREG',     r'\bST\b'              ),
    ( 'COMMA',     r','                   ), # comma delimits operands
    ( 'DECIMAL',   r'[0-9]+'              ), # decimal has no prefix
    ( 'HEX',       r'#[0-9A-F]+'          ), # hex
    ( 'OCTAL',     r'@[0-7]+'             ), # a few PDP folks around in '76
    ( 'BINARY',    r'\$[01\.]+'           ), # $1..1..11
    ( 'STRING',    r"'[^']*'"             ), # basic 'string'
    ( 'EXPOPS',    r'[()+\-~!<>*/&|^%]'   ), # expression stuff
    ( 'WORD',      r'[A-Z0-9_]+'          ), # words that are not reserved
    ( 'COMMENT',   r';.*$'                ), # ; to end of line
    ( 'GARBAGE',   r'.+$'                 )  # something unexpected to end of line
    ]

'''

Transform the token_specs list into one massive regex of the form,

   (?P<token-class-name>regex-to-match-it)|(?P<token-class-name>....

that is, an or-alternation of named match groups. The result is not something
a human would like to edit, but the regex module handles it just fine.

'''

token_expression = '|'.join(
    '(?P<{0}>{1})'.format(t,r) for (t,r) in token_specs
    )

t_rex = regex.compile( token_expression, regex.IGNORECASE | regex.ASCII )

'''
Define a simple Token class. This would be a legitimate use of a
namedTuple, but that is essentially the following in any case.
'''
class Token() :
    def __init__(self, t_type='', t_value=None, t_start=0, t_end=0 ) :
        self.t_type = t_type
        self.t_value = t_value
        self.t_start = t_start
        self.t_end = t_end

'''

    Regexes for statement recognition

After tokenizing using the above, we process the tokens in sequence, and
build up a synopsis, or signature, of the statement composed of one or a few
characters per token. There are a limited number of signatures possible, and
any statement whose signature is not one of them, is automatically invalid.

Labels and comments are not reflected in the signature. OPCODE and DIRECTIVE
tokens go in as themselves ('LD', 'ORG'). Other tokens are converted to the
single letters in the following table. Any token that could be part of an
expression is represented as 'V'. (The actual validity of an expression is
determined in a separate step.)

Thus the signature for "ld v5,31" is "LDR,V" (opcode LD, R for the register,
comma for the comma, V for the decimal token).

'''

summary_chars = {
    'VREG'    : 'R',
    'IREG'    : 'I',
    'KREG'    : 'K',
    'DTREG'   : 'T',
    'DSREG'   : 'S',
    'COMMA'   : ',',
    'WORD'    : 'V',
    'DECIMAL' : 'V',
    'HEX'     : 'V',
    'OCTAL'   : 'V',
    'BINARY'  : 'V',
    'STRING'  : 'Z',
    'EXPOPS'  : 'V'
    }

'''

Among the resulting signatures, any that do not end with an expression are
simple literals with no varying parts. For quick recognition these are filed
in this dict. The key is the signature string; and the value, a code for the
instruction format.

'''
signature_dict = {
    'ADDI,R' : 'ADDI',
    'ADDR,R' : 'ADDR',
    'ANDR,R' : 'AND',
    'CLS'    : 'CLS',
    'EXIT'   : 'EXIT',
    'HIGH'   : 'HIGH',
    'LDCI,R' : 'LDC',
    'LDHI,R' : 'LDH',
    'LDR,K'  : 'LDK',
    'LDMR'   : 'LDM',
    'LDR,R'  : 'LDRR',
    'LDR,T'  : 'LDRT',
    'LDS,R'  : 'LDSR',
    'LDT,R'  : 'LDTR',
    'LOW'    : 'LOW',
    'ORR,R'  : 'OR',
    'RET'    : 'RET',
    'SCL'    : 'SCL',
    'SCR'    : 'SCR',
    'SER,R'  : 'SER',
    'SHRR,R' : 'SHR',
    'SHLR,R' : 'SHL',
    'SKPR'   : 'SKP',
    'SKNPR'  : 'SKNP',
    'SNER,R' : 'SNER',
    'STDR'   : 'STD',
    'STMR'   : 'STM',
    'SUBR,R' : 'SUB',
    'SUBNR,R' : 'SUBN',
    'XORR,R' : 'XOR'
    }

'''
The remaining possible signatures end in varying amounts of expression
values. We use regexes to recognize these.

Constructed similarly to the token regex above, this regex recognizes only
valid signatures. The name of a match is a code for that instruction format.

The regex is applied with re.fullmatch() so these expressions are
implicitly '^..$'.

'''

signatures = [
    ( 'ADDB',  'ADDR,V+'),
    ( 'CALL',  'CALLV+' ),
    ( 'DA',    'DAZ+'   ),
    ( 'DB',    'DBV+(,V+)*'  ),
    ( 'DRAW',  'DRAWR,R,V+' ),
    ( 'DS',    'DSV+'   ),
    ( 'DW',    'DWV+(,V+)*' ),
    ( 'EQU',   'EQUV+'  ),
    ( 'JPADR', 'JPV+'   ),
    ( 'JPXADR','JPR,V+' ),
    ( 'LDI',   'LDI,V+' ),
    ( 'LDRB',  'LDR,V+' ),
    ( 'ORG',   'ORGV+'  ),
    ( 'RND',   'RNDR,[V+]' ),
    ( 'SCD',   'SCDV+'  ),
    ( 'SEB',   'SER,V+' ),
    ( 'SNEB',  'SNER,V+'),
    ]

signature_expression = '|'.join(
    '(?P<{0}>{1})'.format(t,r) for (t,r) in signatures
    )
signature_regex = regex.compile( signature_expression )


'''
    Assembly-time Symbol Table

Expressions are translated into Python expressions. Each WORD token is
translated into a call on LOOKUP(word).

The name LOOKUP is resolved as a global at the time the eval() function is
applied. When that is done in the namespace of this module, LOOKUP() is the
following, which just returns a one (to avoid unintentional divide-by-zero
errors).

During the real assembly (in the assembler2 module), LOOKUP is defined
to return the value of a name, or None if the name is not defined.

'''

def LOOKUP( name:str ) -> int :
    return 1

'''
    Parsing Phase 1: Recognition

This phase of parsing is called from the QSyntaxHighligher.

For this application we do not need to parse a general-purpose language, but
only recognize a relatively small set of valid statement forms. The only
complicated part is that we are supposed to support expressions. Both the
CHIPPER assembler and Jeffrey Bian's MOCHI-8 assembler support general
expressions, so presumably there are CHIP-8 source programs around that use
them. Probably 99% of all expressions are:

* a single literal value like #02f or $10001000
* a single name like DO_SUB
* two values with one operator between,like NAME & #0f.

Nevertheless we need to handle ones like (to concoct a ridiculous example),

    LD V2, (BUFEND - BUFSIZE) & ( #073 < 2 ) % 7

I considered taking this as an opportunity to write my own parser for
expressions -- but no. There are only cosmetic differences between CHIPPER
literals and Python ones (#073 vs. 0x073, $10001000 vs. b'10001000', shift
and exponent operators) and once those are fixed, we can use Python's
perfectly good parser on them.

So, phase 1 of parsing proceeds in these steps:

    * Initialize the Statement object for parsing.

    * Tokenize the statement with the t_rex regex, producing a list
      of tokens.

    * Strip off a label (LABEL token or WORD EQU), noting the label in S.defined_name

    * Strip off a COMMENT token, which will be the last if it exists.

    * If there are no tokens left (statement is only a label and/or a comment)
      set S.is_valid and return.

    * Scan the remaining list of tokens to do two things:

      - Build a signature of the statement.

      - Save the tokens of expression operands as lists of tokens.

    * Check the signature against signature_dict and signature_regex. If it
      doesn't match, return S with is_valid False.

    * Store the form of the statement yielded by signature_dict/signature_regex.

    * Convert any expression(s) into Python form, apply compile() to them.

    * If compile() reports an error, return S with is_valid False.

    * Store the code object(s) in S.expressions for use at assembly time.

    * Set the assembled length of the instruction based on opcode and operands.

    * Set S.is_valid to True

Error handling: a number of errors are detected. For each we leave a message
text in S.error_msg and, when it is known, the start of the bad token in
S.error_pos. It is up to the caller to convey this info to the user.

'''

def phase_one( statement_text: str, S : Statement ) :
    global LOOKUP

    '''
    Clear the Statement fields we will set here.
    '''
    S.init_static()
    '''
    Tokenize the text to get a list of tokens.
    '''
    tokens = []
    for match in regex.finditer( t_rex, statement_text ) :

        '''
        Ignore whitespace tokens and comments, don't even put them
        in the list.
        '''
        if match.lastgroup == 'WHITE' or match.lastgroup == 'COMMENT' :
            continue

        '''
        If something is unrecognizable, the regex falls through to the
        catch-all GARBAGE token. Just mark the statement bad and quit
        '''
        if match.lastgroup == 'GARBAGE' :
            S.text_error = True
            S.error_pos = match.start( match.lastgroup )
            S.error_msg = 'Cannot parse statement'
            break

        '''
        If this is a STRING token and the one just prior was also, we
        have the situation of 'MA''AM', the doubled single quote, which
        tokenized as STRING('MA') STRING('AM'). Put the parts back together
        in that preceding token, removing one single-quote.
        '''
        if match.lastgroup == 'STRING' \
           and tokens \
           and tokens[-1].t_type == 'STRING' :
            tokens[-1].t_value = tokens[-1].t_value[:-1] + "'" + match.group( token_type )[1:]
            continue

        '''
        Save this recognizable token with its type, value and start/end position.
        If it is a word token, uppercase it now.
        '''
        token_type = match.lastgroup
        token_value = match.group( token_type )
        if token_type == 'WORD' :
            token_value = token_value.upper()
        token_start, token_end = match.span( token_type )
        tokens.append( Token( token_type, token_value, token_start, token_end ) )

    '''
    If the tokens were not all recognized, quit now
    '''
    if S.text_error :
        return

    '''
    If the statement defines a label, note that and strip it.
    '''
    if len(tokens) and tokens[0].t_type == 'LABEL' :
            '''
            Normal label: Extract the name from the match. The match includes \s*
            before and after the word, and the colon that ends it. So take off the
            colon and strip any leading and trailing spaces, and uppercase it.
            '''
            S.defined_name = tokens[0].t_value[:-1].strip().upper()
            '''
            That "implements" the label (S.defined_value will be filled in
            during assembler2 time). Discard the label token.
            '''
            tokens = tokens[1:]
    elif len(tokens) >= 3 \
         and tokens[0].t_type == 'WORD' \
         and tokens[1].t_type == 'DIRECTIVE' \
         and ( 'EQU' == tokens[1].t_value.upper() or '=' == tokens[1].t_value ) :
            '''
            WORD EQU expression (well, probably an expression, assume it is
            for now). Strip only the word, storing it in S. Leave
            S.defined_value None. Also, normalize the EQU to a single form.
            '''
            tokens[1].t_value = 'EQU' # in case it said "="
            S.defined_name = tokens[0].t_value
            tokens = tokens[1:]

    '''
    If the whole line was just a label and/or a comment, we are done.
    '''
    if 0 == len( tokens ) :
        return

    '''
    Build the signature while storing register indices and expression
    tokens for later use.

    At this point the token list cannot have WHITE, COMMENT or GARBAGE
    tokens. It should not have a COLON token, but could (as an error).
    It should have a single leading OPCODE or DIRECTIVE (but might not,
    or might have two or more). All other possible token types are
    listed in summary_chars.

    Coding note: appending a char to a string requires copying the string.
    Appending a char to a list does not. So we build up the signature as
    a list of chars, then join it to make a search key.
    '''
    signature = []
    expression = []
    for token in tokens :
        '''
        The values of OPCODE or DIRECTIVE tokens go into the signature
        unchanged. If they are not the first token, or if there are extra
        ones, the lookup later will fail.
        '''
        if token.t_type == 'OPCODE' or token.t_type == 'DIRECTIVE' :
            signature.append( token.t_value.upper() ) # LD or ORG or DRAW
            continue
        '''
        Fetch the summary char for this token type. The only token type
        not in summary_chars is GARBAGE.
        '''
        if not token.t_type in summary_chars :
            S.text_error = True
            S.error_pos = token.t_start
            S.error_msg = 'Invalid token'
            break # out of the loop

        sig_char = summary_chars[ token.t_type ]
        signature.append( sig_char )

        '''
        Handle the register codes, storing them in S.reg_1/2, and
        catching the error of too many or wrong type. Use the summary
        character as a quick way to pick out the reg tokens.

        The K token is not really a register reference.
        '''
        if sig_char == 'K' :
            continue
        if sig_char in 'RITS' :
            code = 0
            if token.t_type == 'VREG' :
                '''
                register codes for v0-vf are their hex values.
                '''
                code = '0123456789ABCDEF'.index( token.t_value.upper()[1] )
            elif token.t_type == 'IREG' :
                code = RCODES.I
            elif token.t_type == 'T' :
                code = RCODES.T
            elif token.t_type == 'DTREG' :
                code = RCODES.T
            elif token.t_type == 'DSREG' :
                code = RCODES.S
            if S.reg_1 is None :
                S.reg_1 = code
            elif S.reg_2 is None :
                S.reg_2 = code
            else :
                S.text_error = True
                S.error_pos = token.t_start
                S.error_msg = 'Invalid register operand'
                break
            continue

        '''
        If the token is a COMMA, it terminates the current expression,
        if there is one. Commas can also appear between register names.
        '''
        if token.t_type == 'COMMA' :
            if expression : # is not an empty list,
                S.expressions.append( expression )
                expression = []
            continue
        '''
        Remaining token types are elements of an expression: numbers,
        words, or operator symbols. Add the token to the current expression.
        '''
        expression.append( token )

    '''
    If any errors were found in that loop, quit now.
    Otherwise, save the (last or only) expression if any.
    '''
    if S.text_error :
        return
    if expression :
        S.expressions.append( expression )
    '''
    Compress the signature to a single string and look it up. It will likely
    be in signature_dict; if not, it should be recognized by signature_regex.
    '''
    instruction_form = None
    signature = ''.join( signature )
    if signature in signature_dict :
        instruction_form = signature_dict[ signature ]
    else :
        m = signature_regex.fullmatch( signature )
        if m : # is not None,
            instruction_form = m.lastgroup
            if instruction_form == 'JPXADR' and S.reg_1 != 0 :
                S.text_error = True
                S.error_pos = 0
                S.error_msg = 'Must use V0'
        else :
            '''
            The statement was composed of recognizable tokens but in some
            order that made no sense, like "STM :V5" or "EQU = 5". In this
            case we know the statement is wrong, so return S now, but
            we do not know where the position of the error is.
            '''
            S.text_error = True
            S.error_pos = 0
            S.error_msg = 'Statement does not make sense'

    '''
    Any errors in the signature check? If so, quit.
    '''
    if S.text_error :
        return

    '''
    We know the instruction form code; store it in S.form for use
    during the assembly.
    '''
    S.form = instruction_form

    '''
    The statement looks valid so far but we have not actually parsed the
    expression(s) if any. They are stowed in S.expressions as a list of
    lists of tokens.

    For each expression, translate the tokens to Python syntax to form a Python
    expression text. Use the built-in compile() function to parse and convert
    that to a code-object that can be evaluated later.

    Literals need only a cosmetic brush-up except two cases: string literals,
    need to be uppercased and converted to bytes('string',encoding=ASCII).
    Decimal literals need to be checked for the peculiar problem that Python
    3 does not allow a leading zero on a literal because that would have been
    an octal literal under Python 2. So get rid of leading zeros on decimals.

    Names are converted into calls on the LOOKUP() function. The one in this
    module returns 1 for any name, so a compiled expression can be evaluated
    at this time. (Returns 1 so that in case the user wrote "NAME1/NAME2" we
    do not cause a divide-by-zero.)
    '''

    code_list = []
    for token_list in S.expressions :
        '''
        Again, collect a string as a list of sub-strings, then join at the end.
        '''
        python_expression = []

        for token in token_list :
            if token.t_type == 'DECIMAL' :
                # Decimals are fine except for avoiding a leading 0. However,
                # lstrip can get carried away...
                nonzero_decimal = token.t_value.lstrip('0')
                python_expression.append( nonzero_decimal if len(nonzero_decimal) else '0' )
            elif token.t_type == 'HEX' :
                # #0f -> 0x0f
                python_expression.append( '0x0' + token.t_value[1:] )
            elif token.t_type == 'BINARY' :
                # $...1..1 -> $0001001
                token.t_value = token.t_value.replace('.','0')
                # $0001001 -> b'0001001'
                python_expression.append( "0b" + token.t_value[1:] )
            elif token.t_type == 'OCTAL' :
                # @377 -> 0o377
                python_expression.append( '0o0' + token.t_value[1:] )
            elif token.t_type == 'STRING' :
                # 'ma'am' -> bytes("MA'AM",encoding="ASCII")
                python_expression.append( 'bytes("' + token.t_value[1:-1].upper() + '", encoding="ASCII")' )
            elif token.t_type == 'WORD' :
                # LABEL -> LOOKUP("LABEL")
                python_expression.append( 'LOOKUP("' + token.t_value + '")' )
            else :
                op = token.t_value
                if op in '()+-~*/&|^%' :
                    # ( ) + - ~ * / & | ^ % are python
                    python_expression.append( op )
                elif op == '!' :
                    # 2!4 -> 2**4
                    python_expression.append( '**' )
                elif op == '<' :
                    # < -> <<
                    python_expression.append( '<<' )
                elif op == '>':
                    # > -> >>
                    python_expression.append( '>>' )
                else:
                    assert False # no other tokens could get this far

        python_expression = ' '.join( python_expression )

        try :
            code_obj = None
            code_obj = compile( python_expression, 'chip8ide assembler', 'eval' )
            code_list.append( code_obj )
        except Exception as E :
            '''
            compile() threw an exception, note the error and exit the loop.
            '''
            S.text_error = True
            S.error_msg = 'Invalid expression'
            S.error_pos = token_list[0].t_start
            break

    '''
    Errors? Quit. Else save code objects in S. Copy the list
    so we don't leave S pointing to our local.
    '''
    if S.text_error :
        return

    S.expressions = list( code_list )
    #S.python_text = python_expression # DBG Save last/only expression text
    '''
    If the statement got through all that unscathed it is good -- assuming
    any names it refers to are eventually defined! Now try to figure out how
    many bytes the statement will evaluate to. Also check for a couple of
    other errors.

    The vast majority of statements assemble to 2 bytes, so assume that.
    '''
    S.next_pc = 2
    if S.form == 'ORG' or S.form == 'DS' :
        '''
        ORG and DS are very similar in that they just move the PC. ORG assigns
        to the PC while DS increments it, but we can't know the numeric value
        of either one until the expression is evaluated during assembly.
        '''
        S.next_pc = None
    elif S.form == 'DB' :
        '''
        DB generates one byte per expression.
        '''
        S.next_pc = len( S.expressions )
    elif S.form == 'DW' :
        '''
        DW generates two bytes per expression.
        '''
        S.next_pc = 2 * len( S.expressions )
    elif S.form == 'EQU' :
        '''
        EQU generates nothing
        '''
        S.next_pc = 0
    '''
    And that's parsing phase 1
    '''
    return


'''
Aaaaand we hack up some tests. Lasciate ogne speranza...
'''


if __name__ == '__main__' :

    #from binasm import binasm

    #from PyQt5.QtWidgets import QApplication
    #args = []
    #the_app = QApplication( args )

    def print_S( stmt, S:Statement ) :
        if S.text_error :
            print(
                '{}: {} at {}'.format(
                    stmt, S.error_msg, S.error_pos )
                )
        else:
            print(
                '{} -> form:{} label:{} len:{}'.format(
                    stmt, S.form, S.defined_name, S.next_pc )
                )

    good_statements = [
        ' SCD 1+1',
        ' CLS ; cls',
        ' LOW ; low',
        ' HIGH ; get high',
        ' SCR ;',
        ' SCL ',
        ' DRAW v3, v9, 6',
        ' STd v6',
        ' LDm v6',
        ' stm vd',
        ' ldc i, v3',
        ' ldh I, va',
        ' ld I, #242',
        ' add I, v9',
        'LD ST, v4',
        'LD v3,DT',
        'LD DT, v3',
        'subn v3, v9',
        'shr v0, v0',
        'shl v8, v7',
        '  or v0, v9 ; or',
        ' and v7, v9',
        ' xor ve,VF',
        ' sub v3,v9',
        'RND v6,#07',
        'add v5,$0001',
        'add v8,vf',
        'ld v0,v5',
        'ld v0,0',
        'ld v7,  K',
        'sne v1,v0; yo',
        'skp v5',
        'sknp v5',
        'sne vf, #f',
        'se vb,  vc',
        'se vb, 32',
        'label:      ; lots of white    ',
        '; comment',
        'label:',
        'end: exit',
        '  jp far',
        ' jp v0, far',
        ' call far',
        'ret'
        ]

    directs = [
        ' ORG there',
        'foo = bar',
        'BAR EQU 88 % 7',
        ' ds 16',
        ' DW 0',
        ' DW 1,@02, #03, $010',
        ' DB 1,2,$0011,#004',
        ' DB $..1..1..',
        " da  'ma''am' ",
        " da  'string' ",
        " da '' ",
        ' DB 1',
        ' DB 1,2'
        ]
    bad_statements = [
        'da "not quote"',
        'LÅBEL: ; not ascii',
        'label ld v0,v2 :comment',
        'ld v0,v1,v2',
        'rnd v1,v2',
        'ld v0,2+',
        "ds -5",
        'jp v2,far'
        ]
    S = Statement()

    #for stmt in directs : #good_statements :
        #phase_one( stmt, S )
        #print_S( stmt, S )
    #for stmt in good_statements :
        #phase_one( stmt, S )
        #print_S( stmt, S )
    #for stmt in bad_statements :
        #phase_one( stmt, S )
        #print_S( stmt, S )
    stmt = '  LD V7,07'
    phase_one( stmt, S )
    print_S( stmt, S )