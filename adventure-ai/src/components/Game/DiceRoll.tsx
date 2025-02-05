import React from 'react';
import { Box, Button, Text, VStack } from '@chakra-ui/react';

interface DiceRollProps {
    onRoll: () => void;
    requiredRoll: number | undefined;
    disabled: boolean;
}

const DiceRoll: React.FC<DiceRollProps> = ({ onRoll, requiredRoll, disabled }) => {
    return (
        <Box bg="gray.700" p={4} borderRadius="md">
            <VStack spacing={4}>
                <Text color="white" fontSize="lg" textAlign="center">
                    {requiredRoll ? `Roll ${requiredRoll} or higher to succeed!` : 'Ready to roll?'}
                </Text>
                <Button
                    colorScheme="blue"
                    size="lg"
                    onClick={onRoll}
                    isDisabled={disabled}
                    width="full"
                >
                    Roll the Dice!
                </Button>
            </VStack>
        </Box>
    );
};

export default DiceRoll; 