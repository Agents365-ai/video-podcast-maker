import { Composition } from "remotion";
import { Video } from "../../templates/Video";

export const RemotionRoot: React.FC = () => {
	return (
		<Composition
			id="SmokeTest"
			component={Video}
			durationInFrames={10}
			fps={30}
			width={1920}
			height={1080}
			defaultProps={{ enableAnimations: false }}
		/>
	);
};
