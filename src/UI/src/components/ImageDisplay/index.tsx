import { ImageDisplayWrapper, ImageDisplayImg, ImageControlsWrapper} from "./ImageDisplay.styled";
import { Stack, Switch, Typography } from "@mui/material";
import { useState } from "react";
import Zoom from "react-medium-image-zoom";
import "react-medium-image-zoom/dist/styles.css";

interface ImageDisplayProps {
    showControls: boolean;
    url: string;
    maskUrl: string;
}

export const ImageDisplay = ({
    showControls,
    url,
    maskUrl
}: ImageDisplayProps) => {

    const [showMask, setShowMask] = useState(true);

    return (
    <ImageDisplayWrapper>
        <Zoom>
            <ImageDisplayImg src={showMask && maskUrl.length > 0 ? maskUrl : url} alt="image" />
        </Zoom>
        
        {showControls && (<ImageControlsWrapper>
            <Stack direction="row" alignItems="center">
                <Typography variant="body1" color="primary">
                    Show mask
                </Typography>
                <Switch onChange={(e) => setShowMask(e.target.checked)} checked={showMask}/>
            </Stack>
        </ImageControlsWrapper>)}
    </ImageDisplayWrapper>
)}