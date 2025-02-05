import React from 'react';
import { HStack, Button } from '@chakra-ui/react';

interface DiceRollProps {
    onRoll: () => void;
}

const DiceRoll: React.FC<DiceRollProps> = ({ onRoll }) => {
    return (
        <HStack spacing={4} justify="center">
            <Button
                onClick={onRoll}
                bg="linear-gradient(145deg, #ffd700, #ffa500)"
                color="black"
                _hover={{ opacity: 0.8 }}
                size="lg"
                borderRadius="xl"
                boxShadow="lg"
            >
                Roll Dice
            </Button>
            <Button
                bg="linear-gradient(145deg, #ffd700, #ffa500)"
                color="black"
                _hover={{ opacity: 0.8 }}
                size="lg"
                borderRadius="xl"
                boxShadow="lg"
            >
                Button?
            </Button>
            <Button
                bg="linear-gradient(145deg, #ffd700, #ffa500)"
                color="black"
                _hover={{ opacity: 0.8 }}
                size="lg"
                borderRadius="xl"
                boxShadow="lg"
            >
                Button?
            </Button>
        </HStack>
    );
};

export default DiceRoll; 