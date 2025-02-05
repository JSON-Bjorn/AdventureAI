import React, { useState } from 'react';
import {
    Box,
    Textarea,
    Button,
    VStack
} from '@chakra-ui/react';

interface ActionInputProps {
    onSubmit: (action: string) => void;
    disabled: boolean;
}

const ActionInput: React.FC<ActionInputProps> = ({ onSubmit, disabled }) => {
    const [input, setInput] = useState('');

    const handleSubmit = () => {
        if (input.trim()) {
            onSubmit(input.trim());
            setInput('');
        }
    };

    return (
        <VStack spacing={4} mt={4}>
            <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="What would you like to do?"
                bg="gray.800"
                border="none"
                _focus={{ border: '1px solid', borderColor: 'blue.500' }}
                disabled={disabled}
                rows={4}
            />
            <Button
                colorScheme="blue"
                onClick={handleSubmit}
                isDisabled={disabled || !input.trim()}
                width="full"
            >
                Take Action
            </Button>
        </VStack>
    );
};

export default ActionInput; 