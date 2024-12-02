import {
  VerticalTimeline,
  VerticalTimelineElement,
} from "react-vertical-timeline-component";
import "react-vertical-timeline-component/style.min.css";
import { useEffect, useState } from "react";

export default function TimeSeriesDisplay() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("/tweets.json")
      .then((response) => response.json())
      .then((data) => setData(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  return (
    <VerticalTimeline>
      {data.map((item, index) => (
        <VerticalTimelineElement
          key={index}
          className="vertical-timeline-element--work"
          contentStyle={{ background: "rgb(33, 150, 243)", color: "#fff" }}
          contentArrowStyle={{ borderRight: "7px solid  rgb(33, 150, 243)" }}
          date="item.date"
          iconStyle={{ background: "rgb(33, 150, 243)", color: "#fff" }}
          icon={
            <img
              src="/Tesla_Motors.png"
              alt="Tesla Icon"
              style={{ width: "100%", height: "100%" }}
            ></img>
          }
        >
          <h3 className="vertical-timeline-element-title">{item.title}</h3>
          <h4 className="vertical-timeline-element-subtitle">
            {item.subtitle}
          </h4>
          <p>{item.description}</p>
        </VerticalTimelineElement>
      ))}
    </VerticalTimeline>
  );
}
