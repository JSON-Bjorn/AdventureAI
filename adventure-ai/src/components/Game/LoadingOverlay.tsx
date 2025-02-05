import React from 'react';
import {
    Box,
    Spinner,
    Text,
    VStack,
} from '@chakra-ui/react';

interface LoadingOverlayProps {
    isOpen: boolean;
    message?: string;
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ isOpen, message }) => {
    if (!isOpen) return null;

    return (
        <Box
            position="fixed"
            top={0}
            left={0}
            right={0}
            bottom={0}
            bg="rgba(0, 0, 0, 0.7)"
            display="flex"
            alignItems="center"
            justifyContent="center"
            zIndex={9999}
        >
            <VStack spacing={4}>
                <Spinner size="xl" color="blue.500" />
                <Text color="white">{message || 'Loading...'}</Text>
            </VStack>
        </Box>
    );
};

export default LoadingOverlay; 