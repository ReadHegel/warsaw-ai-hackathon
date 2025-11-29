import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { Stack } from "@mui/material"
import styled from "styled-components"

const Wrapper = styled(Stack)`
    width: fit-content;
    height: calc(90vh - 20px);
    padding: 10px 5px;
    gap: 8px;
    align-content: center;
    justify-content: center;
    align-items: center;
    cursor: pointer;

    &:hover{
        filter: brightness(70%);
    }
`;

interface ImageHidingProps {
    onTrigger: () => void;
}

export const ImageHiding = ({
    onTrigger
}:ImageHidingProps) => {
    return (
        <Wrapper onClick={onTrigger}>
            <ChevronLeftIcon color="primary" />
            <ChevronRightIcon color="primary" />
        </Wrapper> 
    )
}