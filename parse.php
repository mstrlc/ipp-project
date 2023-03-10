<?php

// IPP 2022/23
// Project 1 - Parser of IPPcode23
// Author: Matyas Strelec (xstrel03)

// Global variables for storing regexes used in the script
$var_regex = '/^(GF|TF|LF)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$/';
$label_regex = '/^([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$/';

/**
 * If the number of tokens is not equal to the expected number, exit with error code 23
 * 
 * @param $number - actual number of tokens
 * @param $expected - expected number of tokens
 */
function check_number_of_tokens($number, $expected)
{
    if ($number != $expected) {
        fwrite(STDERR, "Error: Wrong number of arguments! Expected $expected, got $number.\n");
        exit(23);
    }
}

/**
 * Check if the variable given is syntactically correct
 * Else, exit with error code 23
 * 
 * @param $token - token to be checked
 */
function check_var($token)
{
    if (!preg_match($GLOBALS['var_regex'], $token)) {
        fwrite(STDERR, "Error: Invalid variable $token!\n");
        exit(23);
    }
}

/**
 * Check if the label given is syntactically correct
 * Else, exit with error code 23
 * 
 * @param $token - token to be checked
 */

function check_label($token)
{
    if (!preg_match($GLOBALS['label_regex'], $token)) {
        fwrite(STDERR, "Error: Invalid label $token!\n");
        exit(23);
    }
}

/**
 * Check if the symbol given is syntactically correct
 * Else, exit with error code 23
 * 
 * @param $token - token to be checked
 */

function check_symb($token)
{
    // Separate the type and value of the symbol
    $type = explode("@", $token)[0];
    $val = explode("@", $token)[1];

    // First, check if the symbol is not a variable
    // If it is, return as it is syntactically correct
    // If it is not, run more checks for syntax correctness
    if (!preg_match($GLOBALS['var_regex'], $token)) {

        // Check for integers
        if ($type == "int") {
            // Integer can either be simple number, hexademical or octal number, and it cannot be empty
            if (is_numeric($val) || preg_match('/^0[xX][0-9a-fA-F]+(_[0-9a-fA-F]+)*$/', $val) || preg_match('/^0[oO]?[0-7]+(_[0-7]+)*$/', $val) || !empty($val)) {
                return;
            } else {
                fwrite(STDERR, "Error: Invalid symbol $token!\n");
                exit(23);
            }

            // Check for booleans
        } else if ($type == "bool" && ($val == "true" || $val == "false")) {
            return;
        }

        // Check for strings
        else if ($type == "string") {
            // Escape sequences are allowed, but they must be in the correct format
            if (str_contains($val, "\\")) {
                // Count the number of backslashes - '\\' because of escaping in PHP
                $num_of_backslashes = substr_count($val, "\\");
                // Count the number of escape sequences as per the regex
                $regex_matches = 0;
                preg_match_all("/\\\\[0-9]{3}/", $val, $regex_matches);
                // If the number of backslashes is not equal to the number of escape sequences, there is an invalid escape sequence
                // In this case, exit with error code 23
                if ($num_of_backslashes != count($regex_matches[0])) {
                    fwrite(STDERR, "Error: Invalid symbol $token!\n");
                    exit(23);
                } else
                    return;
            }
            return;

        // Check for nil type
        } else if ($type == "nil" && $val == "nil")
            return;

        // Symbol doesn't match any allowed syntax, exit with error code 23
        else {
            fwrite(STDERR, "Error: Invalid symbol $token!\n");
            exit(23);
        }
    }
    // Symbol is a variable, return correct
    else {
        return;
    }
}

/**
 * Check if the type given is one of the allowed types
 * Else, exit with error code 23
 * 
 * @param $token - token to be checked
 */

function check_type($token)
{
    if ($token != "int" && $token != "bool" && $token != "string" && $token != "nil") {
        fwrite(STDERR, "Error: Invalid type $token!\n");
        exit(23);
    }
}

/**
 * Write the XML representation of an argument to stdout
 *  
 * @param $xml - object of the xmlwriter class
 * @param $num - number of the token in operation arguments
 * @param $token - token to be written
 */
function write_arg($xml, $num, $token)
{
    // <var> or <const>
    if (str_contains($token, "@")) {
        $type = explode("@", $token)[0];

        // <var>
        if ($type == "GF" || $type == "TF" || $type == "LF") {
            $type = "var";
            $value = $token;
        }
        // <const>
        else if ($type == "int" || $type == "bool" || $type == "string" || $type == "nil") {
            $value = explode("@", $token)[1];
        }
    }
    // <type> or <label>
    else {
        // <type>
        if ($token == "int" || $token == "bool" || $token == "string" || $token == "nil") {
            $type = "type";
            $value = $token;
        }
        // <label>
        else {
            $type = "label";
            $value = $token;
        }
    }

    // Write the argument to stdout
    xmlwriter_start_element($xml, "arg" . $num);
    xmlwriter_start_attribute($xml, "type");
    xmlwriter_text($xml, $type);
    xmlwriter_end_attribute($xml);
    xmlwriter_text($xml, $value);
    xmlwriter_end_element($xml);
}

/**
 * Print the help message
 */
function print_help()
{
    echo "parse.php (IPP project 2023 - part 1)
    Script of type filter reads the source code in IPPcode23 from the standard input,
    checks the lexical and syntactic correctness of the code and prints the XML representation
    of the program on the standard output.
Usage:
    php8.1 parse.php [--help]
Options:
    --help - prints this help message
Error codes:
    21 - wrong or missing header in the source code written in IPPcode23,
    22 - unknown or wrong opcode in the source code written in IPPcode23,
    23 - other lexical or syntactic error in the source code written in IPPcode23.";
    echo "\n";
}

// https://www.php.net/manual/en/example.xmlwriter-simple.php

// Set error reporting to stderr
ini_set('display_errors', 'stderr');

// Check for the --help argument
if ($argc > 1) {
    if ($argv[1] == "--help") {
        print_help();
        exit(0);
    } else {
        fwrite(STDERR, "Error: Invalid argument!\n");
        exit(10);
    }
}

// Read the input from stdin
$input = file_get_contents('php://stdin');

if (empty(trim($input))) {
    fwrite(STDERR, "Error: Empty input!\n");
    exit(11);
}

// Split the input into lines
$lines = explode("\n", $input);

// Create the XML writer object
$xml = xmlwriter_open_memory();
xmlwriter_set_indent($xml, 1);
xmlwriter_set_indent_string($xml, "\t");

// Write the XML header
xmlwriter_start_document($xml, '1.0', 'UTF-8');
xmlwriter_start_element($xml, 'program');
xmlwriter_start_attribute($xml, 'language');
xmlwriter_text($xml, 'IPPcode23');

// Go through each line and clean up the input
foreach ($lines as $index => &$line) {
    // Remove multiple spaces
    $lines[$index] = preg_replace('!\s+!', ' ', $line);
    // Remove comments
    $lines[$index] = preg_replace("/#.*/", '', $line);
    // Remove leading and trailing spaces
    $lines[$index] = trim($line);
    // Remove empty lines
    if ($line == "")
        unset($lines[$index]);
}

// Reindex the array (no empty lines)
$lines = array_values($lines);

// Check for the header
if ($lines[0] != ".IPPcode23") {
    fwrite(STDERR, "Error: Invalid header!\n");
    exit(21);
}

// Remove the header from the array
$lines = array_slice($lines, 1);

// Order of the instructions
$instruction_order = 1;
// Go through each line and check the syntax and write the XML
foreach ($lines as $line) {
    xmlwriter_start_element($xml, 'instruction');
    xmlwriter_start_attribute($xml, 'order');
    xmlwriter_text($xml, $instruction_order);
    xmlwriter_end_attribute($xml);

    // Tokens are separated by spaces, explode to array
    $tokens = explode(" ", $line);
    $num_of_tokens = count($tokens);
    $instruction = strtoupper($tokens[0]);

    xmlwriter_start_attribute($xml, 'opcode');
    xmlwriter_text($xml, $instruction);
    xmlwriter_end_attribute($xml);

    // Check the syntax of the instruction
    // Different instructions have different number and types of arguments
    switch ($instruction) {
        // 0 arguments
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
            check_number_of_tokens($num_of_tokens, 1);
            break;

        // 1 argument
        // <var>
        case "DEFVAR":
        case "POPS":
            check_number_of_tokens($num_of_tokens, 2);
            check_var($tokens[1]);
            write_arg($xml, 1, $tokens[1]);
            break;

        // <label>
        case "CALL":
        case "LABEL":
        case "JUMP":
            check_number_of_tokens($num_of_tokens, 2);
            check_label($tokens[1]);
            write_arg($xml, 1, $tokens[1]);
            break;

        // <symb>
        case "PUSHS":
        case "WRITE":
        case "EXIT":
        case "DPRINT":
            check_number_of_tokens($num_of_tokens, 2);
            check_symb($tokens[1]);
            write_arg($xml, 1, $tokens[1]);
            break;

        // 2 arguments
        // <var> <symb>
        case "MOVE":
        case "NOT":
        case "INT2CHAR":
        case "STRLEN":
        case "TYPE":
            check_number_of_tokens($num_of_tokens, 3);
            check_var($tokens[1]);
            check_symb($tokens[2]);
            write_arg($xml, 1, $tokens[1]);
            write_arg($xml, 2, $tokens[2]);
            break;

        // <var> <type>    
        case "READ":
            check_number_of_tokens($num_of_tokens, 3);
            check_var($tokens[1]);
            check_type($tokens[2]);
            write_arg($xml, 1, $tokens[1]);
            write_arg($xml, 2, $tokens[2]);
            break;

        // 3 arguments
        // <var> <symb> <symb>
        case "ADD":
        case "SUB":
        case "MUL":
        case "IDIV":
        case "LT":
        case "GT":
        case "EQ":
        case "AND":
        case "OR":
        case "STRI2INT":
        case "CONCAT":
        case "GETCHAR":
        case "SETCHAR":
            check_number_of_tokens($num_of_tokens, 4);
            check_var($tokens[1]);
            check_symb($tokens[2]);
            check_symb($tokens[3]);
            write_arg($xml, 1, $tokens[1]);
            write_arg($xml, 2, $tokens[2]);
            write_arg($xml, 3, $tokens[3]);
            break;

        // <label> <symb> <symb>
        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            check_number_of_tokens($num_of_tokens, 4);
            check_label($tokens[1]);
            check_symb($tokens[2]);
            check_symb($tokens[3]);
            write_arg($xml, 1, $tokens[1]);
            write_arg($xml, 2, $tokens[2]);
            write_arg($xml, 3, $tokens[3]);
            break;

        // No instruction found
        default:
            fwrite(STDERR, "Error: Invalid instruction $instruction!\n");
            exit(22);
    }

    // End the instruction
    xmlwriter_end_element($xml);
    $instruction_order++;
}

// Finish the XML
xmlwriter_end_document($xml);

// Write XML to stdout
echo xmlwriter_output_memory($xml);

?>