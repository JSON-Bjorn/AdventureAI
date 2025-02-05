import React from 'react';
import { Box, Image, Spinner, Center } from '@chakra-ui/react';

interface ImageDisplayProps {
    imageUrl?: string;
    isLoading?: boolean;
}

const ImageDisplay: React.FC<ImageDisplayProps> = ({ imageUrl, isLoading = false }) => {
    return (
        <Box
            bg="gray.800"
            borderRadius="md"
            overflow="hidden"
            position="relative"
            height="100%"
        >
            {isLoading ? (
                <Center height="100%">
                    <Spinner size="xl" color="blue.500" />
                </Center>
            ) : imageUrl ? (
                <Image
                    src={imageUrl}
                    alt="Story scene"
                    objectFit="cover"
                    width="100%"
                    height="100%"
                />
            ) : (
                <Center height="100%" color="gray.500">
                    No image available
                </Center>
            )}
        </Box>
    );
};

export default ImageDisplay; 