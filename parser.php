<?php

$var_regex = "/^(GF|TF|LF)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$/";
$const_regex = "/^(int|bool|string|nil)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$/";
$label_regex = "/^([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$/";
function check_number_of_tokens($number, $expected)
{
    if ($number != $expected)
    {
        fwrite(STDERR, "Error: Wrong number of arguments! Expected $expected, got $number.\n");
        exit(22);
    }
}

function check_var($token)
{
    if(!preg_match($GLOBALS['var_regex'], $token))
    {
        fwrite(STDERR, "Error: Invalid variable $token!\n");
        exit(23);
    }
}

function check_label($token)
{
    if(!preg_match($GLOBALS['label_regex'], $token))
    {
        fwrite(STDERR, "Error: Invalid label $token!\n");
        exit(23);
    }
}

function check_symb($token)
{
    $type = explode("@", $token)[0];
    $val = explode("@", $token)[1];

    if(!preg_match($GLOBALS['var_regex'], $token) &&
       !preg_match($GLOBALS['const_regex'], $token))
    {
        if($type == "int" && is_numeric($val))
            return;
        else if($type == "bool" && ($val == "true" || $val == "false"))
            return;
        else if($type == "string" && preg_match($GLOBALS['label_regex'], $val))
            return;
        else if($type == "nil" && $val == "nil")
            return;
        else
        {
            fwrite(STDERR, "Error: Invalid symbol $token!\n");
            exit(23);
        }
    }
}

function check_type($token)
{
    if($token != "int" && $token != "bool" && $token != "string" && $token != "nil")
    {
        fwrite(STDERR, "Error: Invalid type $token!\n");
        exit(23);
    }
}

function write_arg($xml, $num, $token)
{
    // <var> or <const>
    if(str_contains($token, "@"))
    {
        $type = explode("@", $token)[0];

        // <var>
        if($type == "GF" || $type == "TF" || $type == "LF")
        {
            $type = "var";
            $value = $token;
        }
        // <const>
        else if($type == "int" || $type == "bool" || $type == "string" || $type == "nil")
        {
            $type = $type;
            $value = explode("@", $token)[1];
        }
    }
    // <type> or <label>
    else
    {
        // <type>
        if($token == "int" || $token == "bool" || $token == "string" || $token == "nil")
        {
            $type = "type";
            $value = $token;
        }
        // <label>
        else
        {
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

// https://www.php.net/manual/en/example.xmlwriter-simple.php

ini_set('display_errors', 'stderr');

$input = file_get_contents('php://stdin');
$lines = explode("\n", $input);

$xml = xmlwriter_open_memory();
xmlwriter_set_indent($xml, 1);
$res = xmlwriter_set_indent_string($xml, "\t");

xmlwriter_start_document($xml, '1.0', 'UTF-8');
xmlwriter_start_element($xml, 'program');
xmlwriter_start_attribute($xml, 'language');
xmlwriter_text($xml, 'IPPcode23');

if((preg_replace("/#.*/", "", $lines[0])) != ".IPPcode23")
{
    fwrite(STDERR, "Error: Invalid header!\n");
    exit(21);
}

$instruction_order = 1;
foreach ($lines as $index => $line)
{
    // Remove comments, match everything after '#' until the end of the line
    $line = preg_replace("/#.*/", "", $line);
    // Skip the first line and empty lines
    $line = trim($line);
    if ($index == 0 || $line == "") continue;

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

    switch($instruction)
    {
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
        case "NOT":
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
    
        // Invalid instruction
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