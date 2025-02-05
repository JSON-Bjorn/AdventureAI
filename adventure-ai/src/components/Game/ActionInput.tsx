import React, { useState } from 'react';
import { Input, Button, HStack } from '@chakra-ui/react';

interface ActionInputProps {
    onSubmit: (action: string) => void;
    disabled?: boolean;
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
        <HStack spacing={4} bg="rgb(214, 209, 195)" p={4} borderRadius="md">
            <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Enter your action..."
                bg="white"
                color="black"
                disabled={disabled}
            />
        </HStack>
    );
};

export default ActionInput; 