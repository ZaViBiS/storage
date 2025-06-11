package db

import (
	"encoding/json"
	"fmt"
	"log"
	"sort"
	"time"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

type Data struct {
	ID       uint    `gorm:"primaryKey"`
	Time     float64 `json:"time"`
	Temp     float64 `json:"temp"`
	Hum      float64 `json:"hum"`
	FanSpeed float64 `json:"fan_speed"`
	VPD      float64 `json:"vpd"`
}

func InitDB(path string) (*gorm.DB, error) {
	db, err := gorm.Open(sqlite.Open("data.sqlite3"), &gorm.Config{})
	if err != nil {
		log.Fatal("filed", err)
	}
	err = db.Statement.AutoMigrate(&Data{})
	if err != nil {
		log.Fatal("error", err)
	}
	return db, err
}

func Put(data string, db *gorm.DB) error {
	var sensorData Data
	err := json.Unmarshal([]byte(data), &sensorData)
	if err != nil {
		log.Fatal("error", err)
		return err
	}
	r := db.Create(&sensorData)
	if r.Error != nil {
		log.Fatal("err", r.Error)
		return r.Error
	}
	return nil
}

func GetLast(db *gorm.DB) (json.RawMessage, error) {
	var data Data
	res := db.Last(&data)
	if res.Error != nil {
		log.Fatal("e", res.Error)
		return nil, res.Error
	}
	fmt.Printf("Type: %T\n", data)
	jsonData, err := json.Marshal(data)
	if err != nil {
		return nil, err
	}
	return jsonData, nil
}

func GetFor(db *gorm.DB, forTimeSec int64, timeGapMin int) ([]Data, error) {
	now := time.Now().Unix()
	startTime := now - forTimeSec
	println(startTime)

	var data []Data
	err := db.Where("time > ?", startTime).Order("time").Find(&data).Error
	if err != nil {
		return nil, err
	}

	// if timeGapMin == 1 {
	// 	return data, nil
	// }

	grouped := map[int64][]Data{}
	gapSec := int64(timeGapMin * 60)

	for _, d := range data {
		groupKey := int64(d.Time) / gapSec * gapSec
		grouped[groupKey] = append(grouped[groupKey], d)
	}

	var keys []int64
	for k := range grouped {
		keys = append(keys, k)
	}
	sort.Slice(keys, func(i, j int) bool { return keys[i] < keys[j] })

	var result []Data
	for _, k := range keys {
		group := grouped[k]
		n := float64(len(group))
		if n == 0 {
			continue
		}
		var avg Data
		for _, d := range group {
			avg.Time += d.Time
			avg.Temp += d.Temp
			avg.Hum += d.Hum
			avg.FanSpeed += d.FanSpeed
			avg.VPD += d.VPD
		}
		avg.Time = round(avg.Time / n)
		avg.Temp = round(avg.Temp / n)
		avg.Hum = round(avg.Hum / n)
		avg.FanSpeed = round(avg.FanSpeed / n)
		avg.VPD = round(avg.VPD / n)
		result = append(result, avg)
	}

	return result, nil
}

func round(f float64) float64 {
	return float64(int(f*100)) / 100
}
