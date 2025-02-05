import React from 'react';
import { Box, Text } from '@chakra-ui/react';

const StoryDisplay: React.FC = () => {
    return (
        <Box
            bg="rgb(214, 209, 195)"
            p={6}
            borderRadius="md"
            height="100%"
            overflowY="auto"
        >
            <Text
                fontSize="lg"
                fontFamily="'Courier New', monospace"
                color="black"
                whiteSpace="pre-wrap"
            >
                The condemned noble stands upon the wooden platform, stripped to his waist, head
                bowed and shoulders slumped beneath the weight of his disgrace...
            </Text>
            <Box mt={4}>
                <Text
                    fontSize="lg"
                    fontFamily="'Courier New', monospace"
                    color="black"
                >
                    Your choice:
                </Text>
            </Box>
        </Box>
    );
};

export default StoryDisplay; 