import {
  VerticalTimeline,
  VerticalTimelineElement,
} from "react-vertical-timeline-component";
import "react-vertical-timeline-component/style.min.css";
import { useEffect, useState } from "react";

export default function TimeSeriesDisplay() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("/tweets_with_classes.json")
      .then((response) => response.json())
      .then((data) => {
        const dataArray = Object.keys(data).map((key) => ({
          text: key,
          class: data[key],
        }));
        setData(dataArray);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  return (
    <VerticalTimeline>
      {data.map((item, index) => {
        let backgroundColor;
        console.log(item);
        switch (item.class.class) {
          case "Positive":
            backgroundColor = "green";
            break;
          case "Neutral":
            backgroundColor = "gray";
            break;
          case "Negative":
            backgroundColor = "red";
            break;
          default:
            backgroundColor = "blue";
        }

        return (
          <VerticalTimelineElement
            key={index}
            className="vertical-timeline-element--work"
            contentStyle={{ background: backgroundColor, color: "#000" }}
            contentArrowStyle={{ borderRight: `7px solid ${backgroundColor}` }}
            date={item.class.date}
            iconStyle={{ background: "rgb(33, 150, 243)", color: "#000" }}
            icon={
              <img
                src="/Tesla_Motors.png"
                alt="Tesla Icon"
                style={{ width: "100%", height: "100%" }}
              ></img>
            }
          >
            <h3 className="vertical-timeline-element-title">
              {item.class.title}
            </h3>
            <p>{item.class.description}</p>
          </VerticalTimelineElement>
        );
      })}
    </VerticalTimeline>
  );
}
