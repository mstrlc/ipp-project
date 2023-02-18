<?php

$var_regex = '/^(GF|TF|LF)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$/';
$label_regex = '/^([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$/';

function check_number_of_tokens($number, $expected)
{
    if ($number != $expected) {
        fwrite(STDERR, "Error: Wrong number of arguments! Expected $expected, got $number.\n");
        exit(23);
    }
}

function check_var($token)
{
    if (!preg_match($GLOBALS['var_regex'], $token)) {
        fwrite(STDERR, "Error: Invalid variable $token!\n");
        exit(23);
    }
}

function check_label($token)
{
    if (!preg_match($GLOBALS['label_regex'], $token)) {
        fwrite(STDERR, "Error: Invalid label $token!\n");
        exit(23);
    }
}

function check_symb($token)
{
    $type = explode("@", $token)[0];
    $val = explode("@", $token)[1];

    if (!preg_match($GLOBALS['var_regex'], $token)) {
        if ($type == "int" && is_numeric($val))
            return;
        else if ($type == "bool" && ($val == "true" || $val == "false"))
            return;
        else if ($type == "string") {
            if (str_contains($val, "\\")) {
                $num_of_backslashes = substr_count($val, "\\");
                $regex_matches = 0;
                preg_match_all("/\\\\[0-9]{3}/", $val, $regex_matches);
                if ($num_of_backslashes != count($regex_matches[0])) {
                    fwrite(STDERR, "Error: Invalid symbol $token!\n");
                    exit(23);
                } else
                    return;
            }
            return;
        } else if ($type == "nil" && $val == "nil")
            return;
        else {
            fwrite(STDERR, "Error: Invalid symbol $token!\n");
            exit(23);
        }
    }
}

function check_type($token)
{
    if ($token != "int" && $token != "bool" && $token != "string" && $token != "nil") {
        fwrite(STDERR, "Error: Invalid type $token!\n");
        exit(23);
    }
}

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

    xmlwriter_start_element($xml, "arg" . $num);
    xmlwriter_start_attribute($xml, "type");
    xmlwriter_text($xml, $type);
    xmlwriter_end_attribute($xml);
    xmlwriter_text($xml, $value);
    xmlwriter_end_element($xml);
}

function print_help()
{
    echo "parse.php (IPP projekt 2023 - 1. cast)
    Skript typu filtr nacte ze standardniho vstupu zdrojovy kod v IPPcode23,
    zkontroluje lexikalni a syntaktickou spravnost kodu a vypise na standardni
    vystup XML reprezentaci programu.
Pouziti:
    php8.1 parse.php [--help]
Prepinace:
    --help - vypise napovedu
Chybove kody:
    21 - chybna nebo chybejici hlavicka ve zdrojovem kodu zapsanem v IPPcode23,
    22 - neznamy nebo chybny operacni kod ve zdrojovem kodu zapsanem v IPPcode23,
    23 - jina lexikalni nebo syntakticka chyba zdrojoveho kodu zapsaneho v IPPcode23.";
    echo "\n";
}

// https://www.php.net/manual/en/example.xmlwriter-simple.php

ini_set('display_errors', 'stderr');

if ($argc > 1) {
    if ($argv[1] == "--help") {
        print_help();
        exit(0);
    } else {
        fwrite(STDERR, "Error: Invalid argument!\n");
        exit(10);
    }
}

$input = file_get_contents('php://stdin');
if (empty(trim($input))) {
    fwrite(STDERR, "Error: Empty input!\n");
    exit(11);
}

$lines = explode("\n", $input);

$xml = xmlwriter_open_memory();
xmlwriter_set_indent($xml, 1);
$res = xmlwriter_set_indent_string($xml, "\t");

xmlwriter_start_document($xml, '1.0', 'UTF-8');
xmlwriter_start_element($xml, 'program');
xmlwriter_start_attribute($xml, 'language');
xmlwriter_text($xml, 'IPPcode23');


foreach ($lines as $index => &$line) {
    $lines[$index] = preg_replace('!\s+!', ' ', $line);
    $lines[$index] = preg_replace("/#.*/", '', $line);
    $lines[$index] = trim($line);
    if ($line == "")
        unset($lines[$index]);
}

$lines = array_values($lines);

if ($lines[0] != ".IPPcode23") {
    fwrite(STDERR, "Error: Invalid header!\n");
    exit(21);
}

$lines = array_slice($lines, 1);

$instruction_order = 1;
foreach ($lines as $line) {
    xmlwriter_start_element($xml, 'instruction');
    xmlwriter_start_attribute($xml, 'order');
    xmlwriter_text($xml, $instruction_order);
    xmlwriter_end_attribute($xml);

    $tokens = explode(" ", $line);
    $num_of_tokens = count($tokens);
    $instruction = strtoupper($tokens[0]);

    xmlwriter_start_attribute($xml, 'opcode');
    xmlwriter_text($xml, $instruction);
    xmlwriter_end_attribute($xml);

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
        default:
            fwrite(STDERR, "Error: Invalid instruction $instruction!\n");
            exit(22);
    }

    xmlwriter_end_element($xml);
    $instruction_order++;
}

xmlwriter_end_document($xml);
echo xmlwriter_output_memory($xml);

?>