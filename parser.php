<?php

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

// Check if the first line is a valid header
if ($lines[0] != ".IPPcode23")
{
    fwrite(STDERR, "Error: Invalid header!\n");
    exit(21);
}

// Go through all lines
$instruction_order = 1;
foreach ($lines as $index => $line)
{
    // Skip the first line
    if ($index == 0)
        continue;

    // Remove comments
    $line = preg_replace("/#.*/", "", $line); // Match everything after '#' until the end of the line
    
    // Skip empty lines
    if (trim($line) == "")
        continue;

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
            if ($num_of_tokens != 1)
            {
                fwrite(STDERR, "Error: Wrong number of arguments!\n");
                exit(22);
            }
            break;
            
        // 1 argument

        // <var>
        case "DEFVAR":
        case "POPS":
            if ($num_of_tokens != 2)
            {
                fwrite(STDERR, "Error: Wrong number of arguments!\n");
                exit(22);
            }
            if(preg_match("/^(G|T|L)F@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$/", $tokens[1]))
            {
                xmlwriter_start_element($xml, 'arg1');
                xmlwriter_start_attribute($xml, 'type');
                xmlwriter_text($xml, 'var');
                xmlwriter_end_attribute($xml);
                xmlwriter_text($xml, $tokens[1]);
                xmlwriter_end_element($xml);
            }
            else
            {
                fwrite(STDERR, "Error: Invalid variable name at $tokens[1]!\n");
                exit(23);
            }
            break;

        // <label>
        case "CALL":
        case "LABEL":
        case "JUMP":
            if ($num_of_tokens != 2)
            {
                fwrite(STDERR, "Error: Wrong number of arguments!\n");
                exit(22);
            }
            if(preg_match("/^([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$/", $tokens[1]))
            {
                xmlwriter_start_element($xml, 'arg1');
                xmlwriter_start_attribute($xml, 'type');
                xmlwriter_text($xml, 'var');
                xmlwriter_end_attribute($xml);
                xmlwriter_text($xml, $tokens[1]);
                xmlwriter_end_element($xml);
            }
            else
            {
                fwrite(STDERR, "Error: Invalid variable name at $tokens[1]!\n");
                exit(23);
            }
            break;

        // <symb>
        case "PUSHS":
        case "WRITE":
        case "EXIT":
        case "DPRINT":
            if ($num_of_tokens != 2)
            {
                fwrite(STDERR, "Error: Wrong number of arguments!\n");
                exit(22);
            }
            // if(preg_match("/^(int|bool|string|nil)@()")
            // {
            //     xmlwriter_start_element($xml, 'arg1');
            //     xmlwriter_start_attribute($xml, 'type');
            //     xmlwriter_text($xml, 'var');
            //     xmlwriter_end_attribute($xml);
            //     xmlwriter_text($xml, $tokens[1]);
            //     xmlwriter_end_element($xml);
            // }

            // xmlwriter_start_element($xml, 'arg1');
            // xmlwriter_start_attribute($xml, 'type');
            // xmlwriter_text($xml, 'TODO');
            // xmlwriter_end_attribute($xml);
            // xmlwriter_text($xml, 'TODO');
            // xmlwriter_end_element($xml);
            break;

        // // 2 arguments
        // case "MOVE":
        // case "INT2CHAR":
        // case "STRLEN":
        // case "TYPE":
        // case "NOT":
        // case "READ":
        //     xmlwriter_start_element($xml, 'arg1');
        //     xmlwriter_start_attribute($xml, 'type');
        //     xmlwriter_text($xml, 'TODO');
        //     xmlwriter_end_attribute($xml);
        //     xmlwriter_text($xml, 'TODO');
        //     xmlwriter_end_element($xml);

        //     xmlwriter_start_element($xml, 'arg2');
        //     xmlwriter_start_attribute($xml, 'type');
        //     xmlwriter_text($xml, 'TODO');
        //     xmlwriter_end_attribute($xml);
        //     xmlwriter_text($xml, 'TODO');
        //     xmlwriter_end_element($xml);
        //     break;

        // // 3 arguments
        // case "ADD":
        // case "SUB":
        // case "MUL":
        // case "IDIV":
        // case "LT":
        // case "GT":
        // case "EQ":
        // case "AND":
        // case "OR":
        // case "STRI2INT":
        // case "CONCAT":
        // case "GETCHAR":
        // case "SETCHAR":
        // case "JUMPIFEQ":
        // case "JUMPIFNEQ":
        //     xmlwriter_start_element($xml, 'arg1');
        //     xmlwriter_start_attribute($xml, 'type');
        //     xmlwriter_text($xml, 'TODO');
        //     xmlwriter_end_attribute($xml);
        //     xmlwriter_text($xml, 'TODO');
        //     xmlwriter_end_element($xml);

        //     xmlwriter_start_element($xml, 'arg2');
        //     xmlwriter_start_attribute($xml, 'type');
        //     xmlwriter_text($xml, 'TODO');
        //     xmlwriter_end_attribute($xml);
        //     xmlwriter_text($xml, 'TODO');
        //     xmlwriter_end_element($xml);

        //     xmlwriter_start_element($xml, 'arg3');
        //     xmlwriter_start_attribute($xml, 'type');
        //     xmlwriter_text($xml, 'TODO');
        //     xmlwriter_end_attribute($xml);
        //     xmlwriter_text($xml, 'TODO');
        //     xmlwriter_end_element($xml);
        //     break;

    }

    xmlwriter_end_element($xml);

    $instruction_order++;
}



// // A first element
// xmlwriter_start_element($xml, 'tag1');

// // Attribute 'att1' for element 'tag1'
// xmlwriter_start_attribute($xml, 'att1');
// xmlwriter_text($xml, 'valueofatt1');
// xmlwriter_end_attribute($xml);

// // Start a child element
// xmlwriter_start_element($xml, 'tag11');
// xmlwriter_text($xml, 'This is a sample text, ä');
// xmlwriter_end_element($xml); // tag11

// xmlwriter_end_element($xml); // tag1

// xmlwriter_start_element($xml, 'testc');
// xmlwriter_text($xml, "test cdata2");
// xmlwriter_end_element($xml); // testc

// // A processing instruction
// xmlwriter_start_pi($xml, 'php');
// xmlwriter_text($xml, '$foo=2;echo $foo;');
// xmlwriter_end_pi($xml);

xmlwriter_end_document($xml);
echo xmlwriter_output_memory($xml);

?>