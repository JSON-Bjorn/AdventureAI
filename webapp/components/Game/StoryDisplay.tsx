import React from 'react';
import { Box, Text, Skeleton } from '@chakra-ui/react';

interface StoryDisplayProps {
    story: string;
    isLoading: boolean;
}

const StoryDisplay: React.FC<StoryDisplayProps> = ({ story, isLoading }) => {
    return (
        <Box
            bg="gray.800"
            p={6}
            borderRadius="lg"
            minH="500px"
            maxH="768px"
            overflowY="auto"
            position="relative"
        >
            {isLoading ? (
                <Skeleton height="20px" />
            ) : (
                <Text
                    fontSize="xl"
                    lineHeight="tall"
                    whiteSpace="pre-wrap"
                >
                    {story}
                </Text>
            )}
        </Box>
    );
};

export default StoryDisplay; 