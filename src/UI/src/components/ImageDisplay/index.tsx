import { ImageDisplayWrapper, ImageDisplayImg, ImageWrapper, ImageControlsWrapper} from "./ImageDisplay.styled";
import DUMMY_IMAGE from '../../assets/DUMMY_IMAGE.png';
import DUMMY_OVERLAY from '../../assets/shrek2.png';
import { Box, Stack, Switch, Typography } from "@mui/material";
import { useState } from "react";

interface ImageDisplayProps {
    showControls: boolean;
}

export const ImageDisplay = ({
    showControls
}: ImageDisplayProps) => {

    const [showMask, setShowMask] = useState(false);

    return (
    <ImageDisplayWrapper>
        <ImageWrapper image={DUMMY_IMAGE}>
            {showMask && (<Box
                component="img"
                src={DUMMY_OVERLAY}
                alt="Overlay"
                sx={{
                    gridArea: "1 / 1",    // same cell → perfect overlap
                    maxHeight: '80vh',
                    overflow: 'hidden'
                }}
            />)}
        </ImageWrapper>
        {showControls && (<ImageControlsWrapper>
            <Stack direction="row" alignItems="center">
                <Typography variant="body1" color="primary">
                    Show mask
                </Typography>
                <Switch onChange={(e) => setShowMask(e.target.checked)}/>
            </Stack>
        </ImageControlsWrapper>)}
    </ImageDisplayWrapper>
)}