import React from 'react';
import { Box, Text } from '@chakra-ui/react';

interface StoryDisplayProps {
    story: string;
}

const StoryDisplay: React.FC<StoryDisplayProps> = ({ story }) => {
    return (
        <Box
            bg="gray.700"
            p={4}
            borderRadius="md"
            overflowY="auto"
            height="100%"
        >
            <Text color="white" fontSize="lg" whiteSpace="pre-wrap">
                {story}
            </Text>
        </Box>
    );
};

export default StoryDisplay; 