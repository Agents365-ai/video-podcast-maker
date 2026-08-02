import { Composition } from "remotion";
import { Video } from "../../../skills/video-podcast-maker/templates/Video";
import { defaultVideoProps } from "../../../skills/video-podcast-maker/templates/Root";

export const RemotionRoot: React.FC = () => {
	return (
		<Composition
			id="SmokeTest"
			component={Video}
			durationInFrames={10}
			fps={30}
			width={1920}
			height={1080}
			defaultProps={{
				...defaultVideoProps,
				enableAnimations: false,
				transitionType: "none",
				transitionDuration: 0,
			}}
		/>
	);
};
