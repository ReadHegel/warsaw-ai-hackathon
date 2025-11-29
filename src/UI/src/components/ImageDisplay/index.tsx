import { ImageDisplayWrapper, ImageDisplayImg} from "./ImageDisplay.styled";
import DUMMY_IMAGE from '../../assets/DUMMY_IMAGE.png';

export const ImageDisplay = () => (
    <ImageDisplayWrapper>
        <ImageDisplayImg 
            src={DUMMY_IMAGE}
            alt='Image'
        />
    </ImageDisplayWrapper>
)